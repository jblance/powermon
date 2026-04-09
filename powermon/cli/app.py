# powermon/cli/app.py

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

import typer
from rich import print

from .compare import compare_protocols
from .deps import Deps, default_deps


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

    app.add_typer(list_app, name="list")
    app.add_typer(ble_app, name="ble")
    app.add_typer(config_app, name="config")

    # ------------------------------------------------------------------
    # Completion + caching helpers (closed over deps for test injection)
    # ------------------------------------------------------------------

    @lru_cache(maxsize=32)
    def cached_protocol(protocol: str) -> Any:
        return deps.get_protocol_definition(protocol)

    def get_protocol_names() -> list[str]:
        try:
            return [p.name.lower() for p in deps.protocol_enum]
        except (TypeError, AttributeError):
            return []

    def complete_protocols(ctx: typer.Context, incomplete: str) -> list[str]:
        inc = (incomplete or "").lower()
        return [p for p in get_protocol_names() if p.startswith(inc)]

    def complete_commands_for_ctx(ctx: typer.Context, incomplete: str) -> list[str]:
        """
        Complete commands based on the protocol already provided in the command line.

        - list commands PROTOCOL            -> ctx.params["protocol"]
        - compare PROTO1 PROTO2 --command   -> ctx.params["proto1"]
        """
        try:
            protocol = ctx.params.get("protocol") or ctx.params.get("proto1")
            if not protocol:
                return []
            proto = cached_protocol(str(protocol).lower())
            inc = incomplete or ""
            return [c for c in proto.command_definitions.keys() if c.startswith(inc)]
        except (AttributeError, KeyError, TypeError):
            return []

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
        deps.list_protocols()

    @list_app.command("commands")
    def list_commands_cmd(
        protocol: str = typer.Argument(
            ...,
            metavar="PROTOCOL",
            help="Protocol name",
            autocompletion=complete_protocols,
        ),
    ) -> None:
        """List available commands for PROTOCOL."""
        deps.list_commands(protocol)

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
        """Generate a configuration file interactively."""
        try:
            deps.generate_config_file()
        except KeyboardInterrupt:
            print("[red]Generation of config file aborted[/red]")

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
        # If you later add `validate_config` to Deps, we’ll use it.
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
            # Best-effort pretty print for Pydantic v1/v2 and plain dicts
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

    return app


def _validate_config_fallback(config_path: Path):
    """
    Fallback config validator used if deps.validate_config isn't provided.

    Loads YAML and validates against powermon.configmodel.config_model.ConfigModel
    (works with Pydantic v1 or v2 style APIs).
    """
    from ruamel.yaml import YAML
    from pyaml_env import parse_config  # ty: ignore[unresolved-import]

    yaml = YAML(typ="safe")
    with config_path.open("r", encoding="utf-8") as f:    
        try:
            data: dict = parse_config(f)
        except yaml.YAMLError as exc:
            raise yaml.YAMLError(f"Error processing yaml file: {exc}") from exc
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Error opening yaml file: {exc}") from exc
        #data = yaml.load(f)

    # Import here to keep CLI import-time light
    from powermon.configmodel.config_model import ConfigModel

    # Pydantic v2: model_validate
    if hasattr(ConfigModel, "model_validate"):
        return ConfigModel.model_validate(data)

    # Pydantic v1: parse_obj / constructor
    if hasattr(ConfigModel, "parse_obj"):
        return ConfigModel.parse_obj(data)

    return ConfigModel(**data)