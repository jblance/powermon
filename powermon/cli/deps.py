from __future__ import annotations
from powermon.protocols import Protocol

from dataclasses import dataclass
from typing import Any, Callable


__all__ = ["Deps", "default_deps"]


@dataclass(frozen=True)
class Deps:
    # i18n + version
    translate: Callable[[str], str]
    version: str
    python_version: Callable[[], str]

    # list commands
    list_protocols: Callable[[], None]
    list_commands: Callable[[str], None]
    list_formats: Callable[[], None]
    list_outputs: Callable[[], None]

    # protocol access
    protocol_enum: Any  # Enum-like: iterable of items with .name
    get_protocol_definition: Callable[[str], Any]
    config_error_type: type[Exception]

    # diff engine
    deepdiff: Callable[..., Any]  # DeepDiff class/callable

    # config generation
    generate_config_file: Callable[[], None]

    # BLE (kwargs-based scan to match existing ble_scan signature)
    ble_reset: Callable[[], None]
    ble_scan: Callable[..., None]


def default_deps() -> Deps:
    """
    Production dependency provider.

    Key principle: keep imports cheap and avoid BLE imports at app creation time.
    BLE is imported lazily inside the callable wrappers.
    """
    from platform import python_version as _python_version
    from deepdiff import DeepDiff as _DeepDiff

    from powermon import tl as _translate
    from powermon.version import __version__ as _version
    from powermon.exceptions import ConfigError as _ConfigError

    from powermon.protocols.protocol import (
        Protocol as _Protocol,
        list_protocols as _list_protocols,
        list_commands as _list_commands,
    )
    from powermon.actions.outputs.formatters import Formatter
    from powermon.actions.outputs.output import Output

    # Config generator (stub for now—replace later with your real implementation)
    def _generate_config_file() -> None:
        from rich import print as rprint
        rprint("[yellow]Generating config file...[/]")
        rprint("[red]THIS NEEDS TO BE DONE[/]")

    # BLE wrappers — import only when called (prevents completion/import-time failures)
    def _ble_reset() -> None:
        from powermon.ports.bleport import ble_reset
        ble_reset()

    def _ble_scan(**kwargs: Any) -> None:
        from powermon.ports.bleport import ble_scan
        ble_scan(**kwargs)

    return Deps(
        translate=_translate,
        version=_version,
        python_version=_python_version,
        list_protocols=_list_protocols,
        list_commands=_list_commands,
        list_formats=Formatter.list_formats,
        list_outputs=Output.list_outputs,
        protocol_enum=_Protocol,
        get_protocol_definition=Protocol.from_name,
        config_error_type=_ConfigError,
        deepdiff=_DeepDiff,
        generate_config_file=_generate_config_file,
        ble_reset=_ble_reset,
        ble_scan=_ble_scan,
    )