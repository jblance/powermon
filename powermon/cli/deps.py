from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Callable, Iterable, TYPE_CHECKING

__all__ = ["Deps", "default_deps"]


if TYPE_CHECKING:
    from powermon.protocols.model import ProtocolDefinition
    # If you have a concrete CommandDefinition type you want to expose, import it here:
    # from powermon.protocols.model import CommandDefinition


@dataclass(frozen=True)
class Deps:
    # i18n + version
    translate: Callable[[str], str]
    version: str
    python_version: Callable[[], str]

    # list commands / protocols (return data; CLI prints/formats it)
    list_protocols: Callable[[], list[Any]]
    list_commands: Callable[[str], Iterable[Any]]
    list_formats: Callable[[], None]
    list_outputs: Callable[[], None]

    # protocol access
    protocol_enum: Any  # Enum-like: iterable of items with .name/.value
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
    Protocol loading can also be expensive (imports definitions); load lazily.

    Any errors importing protocol modules should be surfaced loudly (wrapped as ConfigError).
    """
    from platform import python_version as _python_version
    from deepdiff import DeepDiff as _DeepDiff

    from powermon import tl as _translate
    from powermon.version import __version__ as _version
    from powermon.exceptions import ConfigError as _ConfigError

    from powermon.protocols.types import ProtocolType
    from powermon.outputs.formatters import Formatter
    from powermon.outputs.output import Output

    # ------------------------------------------------------------------
    # Lazy registry construction (imports all protocol definition modules)
    # ------------------------------------------------------------------
    @lru_cache(maxsize=1)
    def _registry():
        """
        Build and cache the ProtocolRegistry.

        Any protocol import/load failure is converted into ConfigError with details.
        """
        try:
            # Import here to avoid protocol imports at app creation time
            from powermon.protocols.catalog import build_registry
            return build_registry(validate=True)
        except Exception as exc:
            # If your catalog defines a ProtocolCatalogError with .failures, surface it nicely.
            # Otherwise, fall back to generic exception formatting.
            detail = None
            failures = getattr(exc, "failures", None)
            if failures:
                # best-effort formatting: each failure may be a dataclass with fields
                lines: list[str] = []
                for f in failures:
                    ptype = getattr(f, "protocol_type", "?")
                    module = getattr(f, "module", "?")
                    error = getattr(f, "error", str(f))
                    lines.append(f"- {ptype} -> {module}: {error}")
                detail = "\n".join(lines)

            if detail:
                raise _ConfigError(
                    "Failed to load one or more protocols:\n" + detail
                ) from exc

            raise _ConfigError(f"Failed to build protocol registry: {exc}") from exc

    def _parse_protocol_type(token: str) -> ProtocolType:
        """
        Accept both:
          - value form: 'pi30'  (ProtocolType value)
          - name form:  'PI30'  (ProtocolType member name)
        """
        t = token.strip()
        if not t:
            raise _ConfigError("Protocol token is empty")

        # Prefer value lookup (StrEnum supports ProtocolType("pi30"))
        try:
            return ProtocolType(t.lower())
        except Exception:
            pass

        # Fall back to name lookup (ProtocolType["PI30"])
        try:
            return ProtocolType[t.upper()]
        except KeyError as exc:
            raise _ConfigError(f"Unknown protocol '{token}'") from exc

    # ------------------------------------------------------------------
    # Public deps: return data (CLI does printing)
    # ------------------------------------------------------------------
    def _list_protocols() -> list[Any]:
        # returns list[ProtocolDefinition] in practice
        return _registry().list_protocols()

    def _list_commands(protocol_token: str) -> Iterable[Any]:
        # returns Iterable[CommandDefinition] in practice
        ptype = _parse_protocol_type(protocol_token)
        return _registry().list_commands(ptype)

    def _get_protocol_definition(protocol_token: str) -> Any:
        # returns ProtocolDefinition in practice
        ptype = _parse_protocol_type(protocol_token)
        return _registry().get(ptype)

    # ------------------------------------------------------------------
    # Config generator (stub for now—replace later with real implementation)
    # ------------------------------------------------------------------
    def _generate_config_file() -> None:
        from rich import print as rprint
        rprint("[yellow]Generating config file...[/]")
        rprint("[red]THIS NEEDS TO BE DONE[/]")

    # ------------------------------------------------------------------
    # BLE wrappers — import only when called (prevents completion/import-time failures)
    # ------------------------------------------------------------------
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
        protocol_enum=ProtocolType,
        get_protocol_definition=_get_protocol_definition,
        config_error_type=_ConfigError,
        deepdiff=_DeepDiff,
        generate_config_file=_generate_config_file,
        ble_reset=_ble_reset,
        ble_scan=_ble_scan,
    )