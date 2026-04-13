# powermon/cli/app.py

from __future__ import annotations

import random
from collections import defaultdict
from functools import lru_cache
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any, Iterable, Optional

import typer
from rich import print
from rich.console import Console
from rich.table import Table

from powermon.protocols.model import SelectorTarget

from .compare import compare_protocols
from .deps import Deps, default_deps

console = Console()


def create_app(deps: Optional[Deps] = None) -> typer.Typer:
    """
    Build and return the Typer app. Tests can pass a fake `Deps` instance
    for full dependency injection and isolation.
    """
    deps = deps or default_deps()

    app = typer.Typer(
        name="powermon-cli",
        no_args_is_help=True,
        help="Power Device Monitoring Utility CLI",
    )

    list_app = typer.Typer(help="List supported features")
    ble_app = typer.Typer(help="Bluetooth Low Energy operations")
    config_app = typer.Typer(help="Configuration management")
    test_app = typer.Typer(help="Run protocol fixture tests")

    app.add_typer(list_app, name="list")
    app.add_typer(ble_app, name="ble")
    app.add_typer(config_app, name="config")
    app.add_typer(test_app, name="test")

    # ------------------------------------------------------------------
    # Completion + caching helpers (closed over deps for test injection)
    # ------------------------------------------------------------------

    @lru_cache(maxsize=32)
    def cached_protocol(protocol: str) -> Any:
        # deps.get_protocol_definition accepts either 'pi30' or 'PI30'
        return deps.get_protocol_definition(protocol)

    def get_protocol_tokens() -> list[str]:
        """
        Tokens suitable for CLI selection and completion.
        Prefer enum values (e.g. 'pi30') because that matches folder/module naming.
        """
        try:
            return [getattr(p, "value", p.name).lower() for p in deps.protocol_enum]
        except (TypeError, AttributeError):
            return []

    def complete_protocols(ctx: typer.Context, incomplete: str) -> list[str]:
        inc = (incomplete or "").lower()
        return [p for p in get_protocol_tokens() if p.startswith(inc)]

    def complete_commands_for_ctx(ctx: typer.Context, incomplete: str) -> list[str]:
        """
        Complete command IDs based on the protocol already provided in the command line.

        - list commands PROTOCOL            -> ctx.params["protocol"]
        - compare PROTO1 PROTO2 --command   -> ctx.params["proto1"]
        """
        try:
            protocol = ctx.params.get("protocol") or ctx.params.get("proto1")
            if not protocol:
                return []

            proto = cached_protocol(str(protocol))
            inc = (incomplete or "").upper()

            commands = getattr(proto, "commands", {}) or {}
            return [cmd_id for cmd_id in commands.keys() if str(cmd_id).upper().startswith(inc)]
        except Exception:
            return []

    # ------------------------------------------------------------------
    # Helpers for list commands formatting
    # ------------------------------------------------------------------

    def _hex_bytes(b: bytes) -> str:
        return " ".join(f"{x:02x}" for x in b)

    def _mixed_ascii_hex(b: bytes) -> str:
        """
        Render bytes as:
          - printable ASCII characters
          - CR/LF/TAB as escapes: \\r, \\n, \\t
          - other non-printables as <hh>
        """
        out: list[str] = []
        for x in b:
            if x == 0x0D:
                out.append("\\r")
            elif x == 0x0A:
                out.append("\\n")
            elif x == 0x09:
                out.append("\\t")
            elif 0x20 <= x <= 0x7E:  # printable ASCII
                out.append(chr(x))
            else:
                out.append(f"<{x:02x}>")
        return "".join(out)


    def _load_fixtures_module(proto: object) -> ModuleType:
        proto_id = getattr(proto, "protocol_id", None)
        if not proto_id:
            raise RuntimeError("ProtocolDefinition has no protocol_id")
        return import_module(f"powermon.protocols.{str(proto_id).lower()}.fixtures")


    def _get_fixture_responses(fixtures_mod: ModuleType) -> dict[str, list[bytes]]:
        responses = getattr(fixtures_mod, "RESPONSES", None)
        if not isinstance(responses, dict):
            raise ValueError("fixtures.py must export RESPONSES: dict[str, list[bytes]]")
        # normalise keys to uppercase for matching
        out: dict[str, list[bytes]] = {}
        for k, v in responses.items():
            if not isinstance(v, list):
                raise ValueError(f"RESPONSES[{k!r}] must be a list[bytes]")
            out[str(k).upper()] = v
        return out

    def _get_fixtures_map(fixtures_mod: ModuleType) -> dict[str, list[Any]]:
        fixtures = getattr(fixtures_mod, "FIXTURES", None)
        if fixtures is None:
            raise ValueError("fixtures.py must export FIXTURES: dict[str, list[CommandFixture]]")
        if not isinstance(fixtures, dict):
            raise TypeError(f"FIXTURES must be a dict (got {type(fixtures)!r})")
        return fixtures

    def _resolve_command_id_exact(proto: object, token: str) -> str:
        """
        Resolve user-supplied command token (any case) to canonical command_id.
        Exact match only (no prefix guessing).
        """
        tok = token.strip()
        if not tok:
            raise typer.BadParameter("Command token is empty")

        commands = getattr(proto, "commands", {}) or {}

        canon_by_upper = {str(cid).upper(): str(cid) for cid in commands.keys()}
        u = tok.upper()

        if u in canon_by_upper:
            return canon_by_upper[u]

        raise typer.BadParameter(f"Command not found (not defined): '{token}'")

    # def _resolve_command_id(proto: object, token: str) -> str:
    #     """
    #     Resolve a command token.

    #     Rules:
    #     - exact match (case-insensitive) -> OK
    #     - unique prefix match -> OK
    #     - no matches -> error: command not found
    #     - multiple matches -> error: ambiguous token
    #     """
    #     tok = token.strip().upper()
    #     if not tok:
    #         raise typer.BadParameter("Command token is empty")

    #     commands = getattr(proto, "commands", {}) or {}
    #     keys = [str(k).upper() for k in commands.keys()]

    #     # exact
    #     if tok in keys:
    #         return tok

    #     # prefix matches
    #     matches = [k for k in keys if k.startswith(tok)]
    #     if len(matches) == 1:
    #         return matches[0]

    #     if len(matches) == 0:
    #         raise typer.BadParameter(f"Command not found: '{token}'")

    #     # ambiguous
    #     raise typer.BadParameter(
    #         f"Ambiguous command token '{token}'. Matches: {', '.join(sorted(matches))}"
    #     )
        
    def _wire_request_bytes(proto: object, req: object) -> bytes:
        """
        Best-effort construction of request bytes for verbose display.

        Uses RequestSpec.build() + proto.framing.crc_func.
        If framing provides a higher-level builder, prefer it.
        """
        framing = getattr(proto, "framing", None)
        if framing is None:
            raise ValueError("Protocol has no framing")

        # Prefer a framing-level builder if it exists (best fidelity)
        for method_name in ("build_request", "encode_request", "frame_request", "wrap_request"):
            fn = getattr(framing, method_name, None)
            if callable(fn):
                out = fn(req)
                if not isinstance(out, (bytes, bytearray)):
                    raise TypeError(
                        f"{type(framing).__name__}.{method_name} returned {type(out)!r}, expected bytes"
                    )
                return bytes(out)

        # Fallback: use RequestSpec.build() with framing crc_func
        crc_func = getattr(framing, "crc_func", None)
        if not callable(crc_func):
            raise ValueError("Protocol framing has no crc_func")

        build = getattr(req, "build", None)
        if not callable(build):
            raise ValueError("RequestSpec has no build()")

        out = build(crc_func=crc_func, payload=None)
        if not isinstance(out, (bytes, bytearray)):
            raise TypeError(f"RequestSpec.build returned {type(out)!r}, expected bytes")
        return bytes(out)

    # Import CommandCategory lazily to keep import-time light for the CLI
    def _command_category_enum():
        from powermon.protocols.model import CommandCategory
        return CommandCategory

    def _category_title(cat: Any) -> str:
        CommandCategory = _command_category_enum()
        mapping = {
            CommandCategory.IDENTITY: "Identity",
            CommandCategory.METRIC: "Metrics",
            CommandCategory.ACCUMULATOR: "Accumulators",
            CommandCategory.STATUS: "Status",
            CommandCategory.CONFIG_READ: "Config (Read)",
            CommandCategory.CONFIG_WRITE: "Config (Write)",
        }
        return mapping.get(cat, str(cat))

    def _callable_name(fn: object) -> str:
        name = getattr(fn, "__name__", None)
        if name:
            return name
        qual = getattr(fn, "__qualname__", None)
        if qual:
            return qual
        cls = getattr(fn, "__class__", None)
        return getattr(cls, "__name__", "callable")

    def _summarise_response(resp: object) -> str:
        parser = getattr(resp, "parser", None)
        crc = bool(getattr(resp, "crc", False))
        minf = getattr(resp, "min_fields", None)
        maxf = getattr(resp, "max_fields", None)

        parser_name = _callable_name(parser) if parser is not None else "?"
        crc_label = "CRC" if crc else "noCRC"

        if minf is None and maxf is None:
            fields = ""
        elif minf == maxf and minf is not None:
            fields = f", fields={minf}"
        else:
            fields = f", fields={minf or 0}..{maxf or '∞'}"

        return f"{parser_name}, {crc_label}{fields}"

    def _selectors_by_command(proto: object) -> dict[str, list[tuple[str, SelectorTarget]]]:
        """
        Returns: {command_id: [(selector_key, SelectorTarget), ...]}
        """
        grouped: dict[str, list[tuple[str, SelectorTarget]]] = defaultdict(list)
        selectors: dict[str, SelectorTarget] = getattr(proto, "selectors", {}) or {}

        for sel_key, target in selectors.items():
            grouped[str(target.command_id)].append((str(sel_key), target))

        for cmd_id in grouped:
            grouped[cmd_id].sort(key=lambda x: x[0])
        return dict(grouped)

    def _truncate_list(items: list[str], max_items: int) -> str:
        if len(items) <= max_items:
            return ", ".join(items)
        return ", ".join(items[:max_items]) + f" (+{len(items) - max_items})"

    def _format_selectors(
        items: Iterable[tuple[str, SelectorTarget]],
        *,
        max_items: int,
    ) -> tuple[str, str, str]:
        """
        Returns: (aliases, reading_selectors, parameter_selectors)

        - alias selectors: neither reading_key nor parameter set
        - reading selectors: reading_key set
            rendered as:
              - key (if key == reading_key)
              - key→reading_key (if different)
        - parameter selectors: parameter set
            rendered as:
              - key (if key == parameter)
              - key→parameter (if different)
        """
        aliases: list[str] = []
        readings: list[str] = []
        params: list[str] = []

        for key, target in items:
            rk = target.reading_key
            param = target.parameter

            if rk is not None and param is not None:
                # Should never happen by invariant, but keep CLI resilient.
                readings.append(f"{key}→{rk}")
                params.append(f"{key}→{param}")
                continue

            if rk is not None:
                readings.append(key if key == rk else f"{key}→{rk}")
            elif param is not None:
                params.append(key if key == param else f"{key}→{param}")
            else:
                aliases.append(key)

        return (
            _truncate_list(aliases, max_items),
            _truncate_list(readings, max_items),
            _truncate_list(params, max_items),
        )

    def _render_commands_table(
        *,
        proto: object,
        protocol: str,
        category: Any,
        commands: list[Any],
        verbose: bool,
        show_selectors: bool,
        selectors_max: int,
        sel_index: dict[str, list[tuple[str, SelectorTarget]]],
    ) -> None:
        title = f"{_category_title(category)} — {protocol} ({len(commands)})"

        CommandCategory = _command_category_enum()
        if category == CommandCategory.CONFIG_WRITE and commands:
            console.print("[bold red]Warning:[/] Config-write commands may change device configuration.\n")

        table = Table(title=title)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Description", style="white")
        table.add_column("SE", justify="center", style="red", no_wrap=True)
        table.add_column("Readings", justify="right", style="green", no_wrap=True)
        table.add_column("Params", justify="right", style="green", no_wrap=True)

        if show_selectors:
            table.add_column("Selectors", style="cyan")
            table.add_column("Reading selectors", style="cyan")
            table.add_column("Parameter selectors", style="cyan")

        if verbose:
            table.add_column("Request (mixed)", style="yellow")
            table.add_column("Request (HEX)", style="yellow")
            table.add_column("Response", style="yellow")

        commands.sort(key=lambda c: getattr(c, "command_id", "") or "")

        for c in commands:
            command_id = getattr(c, "command_id", "") or ""
            name = getattr(c, "name", "") or ""
            desc = getattr(c, "description", "") or ""
            se = "✓" if bool(getattr(c, "side_effects", False)) else ""

            readings = getattr(c, "readings", None) or {}
            parameters = getattr(c, "parameters", None) or {}

            row: list[str] = [
                str(command_id),
                str(name),
                str(desc),
                se,
                str(len(readings)),
                str(len(parameters)),
            ]

            if show_selectors:
                items = sel_index.get(str(command_id), [])
                aliases, reading_selectors, parameter_selectors = _format_selectors(
                    items, max_items=selectors_max
                )
                row.append(aliases)
                row.append(reading_selectors)
                row.append(parameter_selectors)

            if verbose:
                req = getattr(c, "request", None)
                resp = getattr(c, "response", None)

                if req is not None:
                    try:
                        wire = _wire_request_bytes(proto, req)
                        row.append(_mixed_ascii_hex(wire))
                        row.append(wire.hex(" "))
                    except Exception as exc:
                        row.append("")
                        row.append(f"[dim]{exc}[/dim]")
                else:
                    row.append("")
                    row.append("")

                row.append(_summarise_response(resp) if resp is not None else "")

            table.add_row(*row)

        console.print(table)

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    @app.command()
    def version() -> None:
        """Display version information."""
        transl_name = deps.translate("Power Device Monitoring Utility CLI")
        description = (
            f"{transl_name}, version: {deps.version}, "
            f"python version: {deps.python_version()}"
        )
        print(description)

    # ---- list ----

    @list_app.command("protocols")
    def list_protocols_cmd() -> None:
        """List available protocols."""
        protocols = deps.list_protocols()

        table = Table(title="Available Protocols")
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Protocol ID", style="magenta", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Ports", style="cyan")
        table.add_column("Commands", justify="right", style="green")
        table.add_column("Selectors", justify="right", style="green")

        for p in sorted(protocols, key=lambda x: str(getattr(x, "protocol_type", ""))):
            ports = getattr(p, "supported_ports", None)
            ports_str = ", ".join(pt.value for pt in sorted(ports, key=lambda x: x.value)) if ports else ""

            table.add_row(
                str(getattr(p, "protocol_type", "")),
                getattr(p, "protocol_id", "") or "",
                getattr(p, "description", "") or "",
                ports_str,
                str(len(getattr(p, "commands", {}) or {})),
                str(len(getattr(p, "selectors", {}) or {})),
            )

        console.print(table)

    @list_app.command("commands")
    def list_commands_cmd(
        protocol: str = typer.Argument(
            ...,
            metavar="PROTOCOL",
            help="Protocol token (e.g. 'pi30' or 'PI30')",
            autocompletion=complete_protocols,
        ),
        category: Optional[str] = typer.Option(
            None,
            "--category",
            "-c",
            help="Filter to a single category (identity, metric, accumulator, status, config_read, config_write)",
        ),
        verbose: bool = typer.Option(
            False,
            "--verbose",
            "-v",
            help="Show request/response summaries",
        ),
        summary: bool = typer.Option(
            False,
            "--summary",
            help="Show counts per category only",
        ),
        show_selectors: bool = typer.Option(
            False,
            "--selectors",
            help="Show selectors (aliases and reading selectors) that resolve to each command.",
        ),
        selectors_max: int = typer.Option(
            6,
            "--selectors-max",
            help="Max selectors to show per cell before truncating with (+N).",
        ),
    ) -> None:
        """List commands for a protocol (grouped by category)."""
        all_cmds = list(deps.list_commands(protocol))
        proto = cached_protocol(protocol)

        CommandCategory = _command_category_enum()

        # Precompute selector index once if needed
        sel_index: dict[str, list[tuple[str, SelectorTarget]]] = _selectors_by_command(proto) if show_selectors else {}

        # Group commands by category
        grouped: dict[Any, list[Any]] = {cat: [] for cat in CommandCategory}
        for cmd in all_cmds:
            cat = getattr(cmd, "category", None) or CommandCategory.STATUS
            grouped.setdefault(cat, []).append(cmd)

        if summary:
            table = Table(title=f"Command Categories — {protocol}")
            table.add_column("Category", style="cyan")
            table.add_column("Count", justify="right", style="green")

            for cat in CommandCategory:
                table.add_row(_category_title(cat), str(len(grouped.get(cat, []))))
            console.print(table)
            return

        # Filter by category (string -> enum)
        if category:
            cat_token = category.strip().lower()
            selected = None
            for cat in CommandCategory:
                if str(getattr(cat, "value", "")).lower() == cat_token:
                    selected = cat
                    break
            if selected is None:
                raise typer.BadParameter(
                    f"Unknown category '{category}'. "
                    f"Choose from: {', '.join([c.value for c in CommandCategory])}"
                )

            _render_commands_table(
                proto=proto,
                protocol=protocol,
                category=selected,
                commands=grouped.get(selected, []),
                verbose=verbose,
                show_selectors=show_selectors,
                selectors_max=selectors_max,
                sel_index=sel_index,
            )
            return

        # Print all categories in enum order
        for cat in CommandCategory:
            _render_commands_table(
                proto=proto,
                protocol=protocol,
                category=cat,
                commands=grouped.get(cat, []),
                verbose=verbose,
                show_selectors=show_selectors,
                selectors_max=selectors_max,
                sel_index=sel_index,
            )

    @list_app.command("formats")
    def list_formats_cmd() -> None:
        """List available output formats."""
        deps.list_formats()

    @list_app.command("outputs")
    def list_outputs_cmd() -> None:
        """List available output modules."""
        deps.list_outputs()

    # ---- compare ----

    @app.command()
    def compare(
        proto1: str = typer.Argument(
            ...,
            help="First protocol",
            autocompletion=complete_protocols,
        ),
        proto2: str = typer.Argument(
            ...,
            help="Second protocol",
            autocompletion=complete_protocols,
        ),
        command: Optional[str] = typer.Option(
            None,
            "--command",
            help="Only compare a specific command (completed from proto1)",
            autocompletion=complete_commands_for_ctx,
        ),
    ) -> None:
        """Compare two protocol definitions."""
        spec = f"{proto1},{proto2}"
        if command:
            spec += f":{command}"
        compare_protocols(spec, deps, cached_protocol)

    # ---- config ----

    @config_app.command("generate")
    def generate() -> None:
        """Generate a base configuration file."""
        import sys

        from ruamel.yaml import YAML

        from .config_generate import generate_base_config

        config = generate_base_config()

        yaml = YAML()
        yaml.indent(mapping=2, sequence=4, offset=2)

        data = config.model_dump(
            mode="json",
            exclude_defaults=False,
            exclude_none=True,
        )

        yaml.dump(data, sys.stdout)

    @config_app.command("validate")
    def validate(
        config_path: Path = typer.Argument(
            ...,
            exists=True,
            dir_okay=False,
            readable=True,
            help="Path to configuration file (YAML)",
        ),
        show: bool = typer.Option(
            False,
            "--show",
            help="Print the parsed/normalised config after validation",
        ),
    ) -> None:
        """
        Validate a configuration file against the config model.

        Returns exit code 0 on success, 1 on validation error.
        """
        validate_fn = getattr(deps, "validate_config", None)

        try:
            if callable(validate_fn):
                cfg = validate_fn(config_path)
            else:
                cfg = _validate_config_fallback(config_path)
        except Exception as ex:
            print(f"[red]Config validation failed:[/] {ex}")
            raise typer.Exit(code=1) from ex

        print(f"[green]Config OK:[/] {config_path}")

        if show and cfg is not None:
            try:
                if hasattr(cfg, "model_dump"):
                    data = cfg.model_dump()
                elif hasattr(cfg, "dict"):
                    data = cfg.dict()
                else:
                    data = cfg
            except Exception:
                data = cfg

            print("[bold]Parsed config:[/bold]")
            print(data)

    # ---- ble ----

    @ble_app.command("reset")
    def ble_reset_cmd() -> None:
        """Reset the Bluetooth subsystem."""
        deps.ble_reset()

    @ble_app.command("scan")
    def ble_scan_cmd(
        details: bool = typer.Option(False, "--details", help="Show extra BLE device data"),
        adv_data: bool = typer.Option(False, "--adv-data", help="Include advertisement data"),
        address: Optional[str] = typer.Option(
            None, "--address", metavar="MAC", help="Only scan for supplied MAC address"
        ),
        timeout: float = typer.Option(5.0, "--timeout", help="Scan duration in seconds"),
    ) -> None:
        """Scan for BLE devices."""
        deps.ble_scan(
            details=details,
            adv_data=adv_data,
            address=address,
            get_chars=False,
            timeout=timeout,
        )

    @ble_app.command("get-chars")
    def ble_get_chars_cmd(
        address: str = typer.Option(..., "--address", metavar="MAC", help="Target BLE MAC address"),
        details: bool = typer.Option(True, "--details/--no-details", help="Show device details"),
        timeout: float = typer.Option(5.0, "--timeout", help="Scan duration in seconds"),
    ) -> None:
        """Connect to BLE device(s) and list characteristics."""
        deps.ble_scan(
            details=details,
            adv_data=False,
            address=address,
            get_chars=True,
            timeout=timeout,
        )

    @test_app.command("run")
    def test_fixtures_cmd(
        protocol: str = typer.Argument(
            ...,
            metavar="PROTOCOL",
            help="Protocol token (e.g. 'pi30')",
            autocompletion=complete_protocols,
        ),
        command: str = typer.Argument(
            ...,
            metavar="COMMAND",
            help="Command id (any case). Must exist in current definitions.",
            autocompletion=complete_commands_for_ctx,
        ),
        fixture: Optional[int] = typer.Option(
            None,
            "--fixture",
            "-f",
            help="Select a specific fixture by 1-based index (see --list).",
        ),
        match: Optional[str] = typer.Option(
            None,
            "--match",
            help="Select a fixture whose description contains this substring (case-insensitive).",
        ),
        seed: Optional[int] = typer.Option(
            None,
            "--seed",
            help="Random seed for deterministic fixture selection (useful for CI).",
        ),
        list_fixtures: bool = typer.Option(
            False,
            "--list",
            help="List available fixtures for the command and exit.",
        ),
        show_raw: bool = typer.Option(True, "--raw/--no-raw", help="Show raw fixture bytes."),
        show_fields: bool = typer.Option(True, "--fields/--no-fields", help="Show parsed fields preview."),
        show_readings: bool = typer.Option(True, "--readings/--no-readings", help="Decode readings if defined."),
    ) -> None:
        """
        Run ONE fixture through a command's response parser/decoder.

        Default behaviour:
        - picks 1 fixture at random
        - use --seed to make selection deterministic
        - use --fixture N or --match TEXT to choose specific fixture

        Examples:
        powermon-cli test run pi30 qpiri
        powermon-cli test run pi30 qpiri --seed 42
        powermon-cli test run pi30 qpiri --fixture 2
        powermon-cli test run pi30 qpiri --match "firmware variant"
        powermon-cli test run pi30 qpiri --list
        """
        proto = cached_protocol(protocol)

        # Exact-only resolution (case-insensitive input -> canonical id)
        cmd_id = _resolve_command_id_exact(proto, command)
        cmd_def = proto.commands[cmd_id]  # type: ignore[index]
        cmd_readings_count = len(cmd_def.readings)

        # Load fixtures module and FIXTURES mapping (required)
        try:
            fixtures_mod = _load_fixtures_module(proto)
            fixtures_map = _get_fixtures_map(fixtures_mod)
        except Exception as exc:
            print(f"[red]Failed to load fixtures for protocol '{proto.protocol_id}':[/] {exc}")
            raise typer.Exit(code=2) from exc

        fixtures = fixtures_map.get(cmd_id, [])
        if not fixtures:
            available = ", ".join(sorted(fixtures_map.keys()))
            print(f"[red]No test data (fixtures) found for {cmd_id}[/]")
            if available:
                print(f"[dim]Available fixture keys: {available}[/]")
            raise typer.Exit(code=1)

        # Optional list mode
        if list_fixtures:
            table = Table(title=f"Fixtures: {proto.protocol_id} {cmd_id} ({len(fixtures)})")
            table.add_column("#", style="cyan", no_wrap=True)
            table.add_column("Description", style="magenta")
            table.add_column("Notes", style="dim")
            for i, fx in enumerate(fixtures, start=1):
                table.add_row(
                    str(i),
                    getattr(fx, "description", "") or "",
                    getattr(fx, "notes", "") or "",
                )
            console.print(table)
            return

        # Select one fixture
        chosen = None

        if fixture is not None:
            if fixture < 1 or fixture > len(fixtures):
                raise typer.BadParameter(f"--fixture must be between 1 and {len(fixtures)}")
            chosen_idx = fixture

        elif match:
            m = match.lower()
            candidates = [fx for fx in fixtures if m in (getattr(fx, "description", "") or "").lower()]
            if not candidates:
                print(f"[red]No fixtures match '{match}'[/]")
                raise typer.Exit(code=1)
            if len(candidates) > 1:
                # If multiple match, pick one deterministically if seed provided; else first
                if seed is not None:
                    rng = random.Random(seed)
                    chosen_idx = rng.choice(range(len(candidates)))
                else:
                    chosen_idx = 0
            else:
                chosen_idx = 0

        else:
            rng = random.Random(seed) if seed is not None else random
            chosen_idx = rng.choice(range(len(fixtures)))
        
        chosen = fixtures[chosen_idx]

        desc = getattr(chosen, "description", "") or ""
        notes = getattr(chosen, "notes", "") or ""
        raw = getattr(chosen, "raw_response", None)

        if not isinstance(raw, (bytes, bytearray)):
            print("[red]Invalid fixture: raw_response is not bytes[/]")
            raise typer.Exit(code=1)

        raw_b = bytes(raw)

        # Parse + (optionally) decode readings
        decode_all = None
        if show_readings:
            try:
                from powermon.protocols.decoding import decode_all as _decode_all
                decode_all = _decode_all
            except Exception:
                decode_all = None

        table = Table(title=f"Fixture test: {proto.protocol_id} {cmd_id}")
        table.add_column("Item", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")

        table.add_row("Fixture", desc)
        table.add_row("Fixture Number", str(chosen_idx))
        if notes:
            table.add_row("Notes", notes)

        if show_raw:
            table.add_row("Raw (mixed)", _mixed_ascii_hex(raw_b))

        frame = raw_b
        payload = frame

        framing = getattr(proto, "framing", None)
        if framing is not None:
            # best-effort: only use if those methods exist
            validate = getattr(framing, "validate", None)
            verify_crc = getattr(framing, "verify_crc", None)
            strip = getattr(framing, "strip", None)

            if callable(validate):
                validate(frame)
            if callable(verify_crc):
                verify_crc(frame)
            if callable(strip):
                payload = strip(frame)

        try:
            parsed = cmd_def.response.parser(payload)
        except Exception as exc:
            table.add_row("Parse", f"[red]{exc.__class__.__name__}: {exc}[/]")
            console.print(table)
            raise typer.Exit(code=1) from exc

        if show_fields:
            fields = getattr(parsed, "fields", []) or []
            table.add_row("Fields count (readings)", f"{len(fields)} ({cmd_readings_count})")
            table.add_row("Fields", ", ".join(fields))

        if show_readings:
            readings_map = getattr(cmd_def, "readings", {}) or {}
            if readings_map and decode_all is not None:
                try:
                    decoded = decode_all(parsed, readings_map)
                    # show first few for compactness
                    items = list(decoded.items())
                    rendered = "\n".join(f"{k}={v}" for k, v in items)
                    #suffix = "" if len(decoded) <= 12 else f" (+{len(decoded)-12})"
                    table.add_row("Readings", rendered)  # + suffix)
                except Exception as exc:
                    table.add_row("Readings", f"[red]{exc.__class__.__name__}: {exc}[/]")
                    console.print(table)
                    raise typer.Exit(code=1) from exc
            elif readings_map and decode_all is None:
                table.add_row("Readings", "[dim]decoder not available[/dim]")
            else:
                table.add_row("Readings", "[dim]no readings defined[/dim]")

        console.print(table)


    return app


def _validate_config_fallback(config_path: Path):
    """
    Fallback config validator used if deps.validate_config isn't provided.

    Loads YAML and validates against powermon._config.PowermonConfig
    (works with Pydantic v1 or v2 style APIs).
    """
    from pyaml_env import parse_config  # ty: ignore[unresolved-import]

    try:
        data: dict = parse_config(str(config_path))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Error opening yaml file: {exc}") from exc
    except Exception as exc:
        raise ValueError(f"Error processing yaml file: {exc}") from exc

    from powermon.config import PowermonConfig

    if hasattr(PowermonConfig, "model_validate"):
        return PowermonConfig.model_validate(data)

    if hasattr(PowermonConfig, "parse_obj"):
        return PowermonConfig.parse_obj(data)

    return PowermonConfig(**data)