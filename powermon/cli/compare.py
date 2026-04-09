# powermon/cli/compare.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from rich import print
from rich.box import SIMPLE_HEAVY
from rich.table import Table

from .deps import Deps


class CompareSpecError(ValueError):
    """Raised when the compare specification is invalid."""


@dataclass(frozen=True)
class CompareSpec:
    proto1: str
    proto2: str
    command: Optional[str] = None


def parse_compare_spec(spec: str) -> CompareSpec:
    """
    Parse a compare spec.

    Supported formats:
      - "proto1,proto2"
      - "proto1,proto2:CMD"

    Whitespace around tokens is ignored. Protocol names are normalized to lowercase.
    """
    spec = (spec or "").strip()
    if "," not in spec:
        raise CompareSpecError(
            'Compare spec must be "proto1,proto2" or "proto1,proto2:CMD"'
        )

    proto_part, cmd_part = (spec.split(":", 1) + [None])[:2]
    proto1_raw, proto2_raw = (proto_part.split(",", 1) + [""])[:2]

    proto1 = proto1_raw.strip().lower()
    proto2 = proto2_raw.strip().lower()
    if not proto1 or not proto2:
        raise CompareSpecError(
            'Compare spec must include two protocols: "proto1,proto2"'
        )

    command = cmd_part.strip() if cmd_part else None
    if command == "":
        command = None

    return CompareSpec(proto1=proto1, proto2=proto2, command=command)


# ----------------------------------------------------------------------
# Compare logic (kept outside create_app for direct unit testing)
# ----------------------------------------------------------------------

def compare_protocols(
    spec: str,
    deps: Deps,
    cached_protocol: Callable[[str], Any],
) -> None:
    """
    Compare two protocols, optionally limited to a single command.

    This function is intentionally free of Typer/Click specifics for unit testing.
    """
    try:
        parsed = parse_compare_spec(spec)
    except CompareSpecError as e:
        print(f"[red]{e}[/]")
        return

    try:
        p1 = cached_protocol(parsed.proto1)
        p2 = cached_protocol(parsed.proto2)
    except deps.config_error_type as ex:
        print(f"[red]ERROR:[/] {ex}")
        return

    print("\n[bold]=====================\n PROTOCOL COMPARISON\n=====================[/bold]")

    if parsed.command:
        _compare_single_command(parsed, p1, p2, deps)
        return

    _compare_full_protocol(parsed, p1, p2, deps)


def _compare_single_command(parsed: CompareSpec, p1: Any, p2: Any, deps: Deps) -> None:
    cmd = parsed.command
    assert cmd is not None

    print(f"Checking command: [bold magenta]{cmd}[/bold magenta]")
    print(f"[blue]Defined in {parsed.proto1}[/]: {cmd in p1.command_definitions}")
    print(f"[cyan]Defined in {parsed.proto2}[/]: {cmd in p2.command_definitions}")

    if cmd not in p1.command_definitions or cmd not in p2.command_definitions:
        return

    show_command_definition_differences(
        p1.command_definitions[cmd],
        p2.command_definitions[cmd],
        deps.deepdiff,
    )


def _compare_full_protocol(parsed: CompareSpec, p1: Any, p2: Any, deps: Deps) -> None:
    cmds1 = p1.command_definitions
    cmds2 = p2.command_definitions

    common = cmds1.keys() & cmds2.keys()
    same_commands: list[str] = []
    diff_commands: list[str] = []

    for command in sorted(common):
        diff = deps.deepdiff(
            cmds1[command],
            cmds2[command],
            ignore_order=True,
            ignore_encoding_errors=True,
        )
        if not diff:
            same_commands.append(command)
        else:
            diff_commands.append(command)

    only_in_2 = sorted(cmds2.keys() - cmds1.keys())
    only_in_1 = sorted(cmds1.keys() - cmds2.keys())

    print(
        f"[blue]{parsed.proto1}[/] has {len(cmds1)} commands\n"
        f"[cyan]{parsed.proto2}[/] has {len(cmds2)} commands"
    )
    print(f"Commands with the same definition in both protocols ({len(same_commands)})\n\t{same_commands}")
    print(
        f"Commands in {parsed.proto2} but not {parsed.proto1} ({len(only_in_2)})\n\t"
        f"[cyan]{only_in_2}[/]"
    )
    print(
        f"Commands in {parsed.proto1} but not {parsed.proto2} ({len(only_in_1)})\n\t"
        f"[blue]{only_in_1}[/]"
    )
    print(f"Commands in both protocols with different config ({len(diff_commands)})\n\t{diff_commands}")

    for command in diff_commands:
        print(f"\n[bold magenta]{command}[/bold magenta]")
        show_command_definition_differences(
            cmds1[command],
            cmds2[command],
            deps.deepdiff,
        )


from rich.table import Table
from rich.box import SIMPLE_HEAVY


def show_command_definition_differences(p1, p2, deepdiff) -> None:
    """
    Render a detailed comparison between two command definitions using a
    state-driven Rich table (directional: Protocol A → Protocol B).
    """
    table = Table(
        title="📦 Command Definition Comparison",
        box=SIMPLE_HEAVY,
        show_lines=True,
        header_style="bold",
    )

    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("State", style="bold", width=10)
    table.add_column("Protocol A", style="blue", overflow="fold")
    table.add_column("Protocol B", style="magenta", overflow="fold")

    def state(a: str, b: str) -> str:
        if not a and not b:
            return "⛔ Missing"
        if a == b:
            return "✅ Match"
        if not a and b:
            return "➕ Added"
        if a and not b:
            return "➖ Removed"
        return "❌ Changed"

    # ------------------------------------------------------------------
    # Top-level command fields
    # ------------------------------------------------------------------

    fields = [
        "description",
        "help_text",
        "category",
        "result_type",
        "regex",
        "aliases",
        "command_type",
        "command_code",
        "command_data",
        "construct",
        "construct_min_response",
    ]

    for field in fields:
        v1 = str(getattr(p1, field, "") or "")
        v2 = str(getattr(p2, field, "") or "")

        table.add_row(
            f"📦 {field}",
            state(v1, v2),
            v1 or "—",
            v2 or "—",
        )

    # ------------------------------------------------------------------
    # Test response count
    # ------------------------------------------------------------------

    t1 = len(getattr(p1, "test_responses", []))
    t2 = len(getattr(p2, "test_responses", []))
    table.add_row(
        "🧪 test_responses (count)",
        "✅ Match" if t1 == t2 else "❌ Changed",
        str(t1),
        str(t2),
    )

    # ------------------------------------------------------------------
    # Reading definition counts
    # ------------------------------------------------------------------

    r1 = p1.reading_definition_count()
    r2 = p2.reading_definition_count()
    table.add_row(
        "📊 reading_definitions (count)",
        "✅ Match" if r1 == r2 else "❌ Changed",
        str(r1),
        str(r2),
    )

    # ------------------------------------------------------------------
    # Reading definition details
    # ------------------------------------------------------------------

    for i in range(min(r1, r2)):
        rd1 = p1.reading_definitions[i]
        rd2 = p2.reading_definitions[i]

        header = f"📐 rd[{i}]: {getattr(rd1, 'description', '')}"
        table.add_row(f"[bold]{header}[/bold]", "", "", "")

        if rd1 == rd2:
            table.add_row("↳ status", "✅ Match", "", "")
            continue

        attrs = [
            "response_type",
            "unit",
            "default",
            "format_template",
            "icon",
            "device_class",
            "component",
        ]

        for attr in attrs:
            a1 = str(getattr(rd1, attr, "") or "")
            a2 = str(getattr(rd2, attr, "") or "")
            if a1 != a2:
                table.add_row(
                    f"🔧 ↳ {attr}",
                    state(a1, a2),
                    a1 or "—",
                    a2 or "—",
                )

        o1 = getattr(rd1, "options", None)
        o2 = getattr(rd2, "options", None)
        if o1 != o2:
            table.add_row(
                "⚙️ ↳ options",
                "❌ Changed",
                str(o1),
                str(deepdiff(o1, o2)),
            )

    # ------------------------------------------------------------------
    # Added / removed reading definitions
    # ------------------------------------------------------------------

    if r1 > r2:
        for i in range(r2, r1):
            table.add_row(
                f"📐 rd[{i}]",
                "➖ Removed",
                "Present",
                "—",
            )

    if r2 > r1:
        for i in range(r1, r2):
            table.add_row(
                f"📐 rd[{i}]",
                "➕ Added",
                "—",
                "Present",
            )

    print(table)
