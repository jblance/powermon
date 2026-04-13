# powermon/protocols/catalog.py
from __future__ import annotations

import traceback as _traceback
from dataclasses import dataclass
from importlib import import_module

from powermon.protocols.model import ProtocolDefinition
from powermon.protocols.registry import ProtocolRegistry
from powermon.protocols.types import ProtocolType


@dataclass(frozen=True)
class ProtocolLoadFailure:
    protocol_type: ProtocolType
    module: str
    error: str
    tb: str | None = None


class ProtocolCatalogError(RuntimeError):
    """Raised when one or more protocols fail to import/load."""

    def __init__(self, failures: list[ProtocolLoadFailure]):
        self.failures = failures
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        lines = ["One or more protocols failed to load:"]
        for f in self.failures:
            lines.append(f"- {f.protocol_type} -> {f.module}: {f.error}")
            if f.tb:
                lines.append("  Traceback:")
                lines.append(_indent(f.tb, "    "))
        return "\n".join(lines)


def _indent(text: str, prefix: str) -> str:
    return "\n".join(prefix + line for line in text.splitlines())


def _definition_module_name(ptype: ProtocolType) -> str:
    # Convention: powermon.protocols.<ptype.value>.definition
    return f"powermon.protocols.{ptype.value}.definition"


def load_all_protocol_definitions(*, include_tracebacks: bool = True) -> list[ProtocolDefinition]:
    """
    Load all ProtocolDefinition objects for every ProtocolType enum member.

    Convention:
      - module: powermon.protocols.<ptype.value>.definition
      - attribute: PROTOCOL (ProtocolDefinition)
    """
    defs: list[ProtocolDefinition] = []
    failures: list[ProtocolLoadFailure] = []

    for ptype in ProtocolType:
        module_name = _definition_module_name(ptype)
        try:
            mod = import_module(module_name)
            proto = getattr(mod, "PROTOCOL")
            if not isinstance(proto, ProtocolDefinition):
                raise TypeError(
                    f"{module_name}.PROTOCOL is {type(proto)!r}, expected ProtocolDefinition"
                )

            # Ensure loaded definition matches the enum member we’re iterating
            if proto.protocol_type != ptype:
                raise ValueError(
                    f"protocol_type mismatch: expected {ptype}, got {proto.protocol_type}"
                )

            defs.append(proto)

        except Exception as exc:
            tb = _traceback.format_exc() if include_tracebacks else None
            failures.append(
                ProtocolLoadFailure(
                    protocol_type=ptype,
                    module=module_name,
                    error=f"{exc.__class__.__name__}: {exc}",
                    tb=tb,
                )
            )

    if failures:
        raise ProtocolCatalogError(failures)

    return defs


def build_registry(*, validate: bool = True, include_tracebacks: bool = True) -> ProtocolRegistry:
    """
    Build a ProtocolRegistry for all implemented protocols.
    Raises ProtocolCatalogError if any protocol fails to import/load.
    """
    defs = load_all_protocol_definitions(include_tracebacks=include_tracebacks)
    reg = ProtocolRegistry(defs)

    # Optional extra validation (if these exist on ProtocolRegistry)
    if validate:
        validate_defs = getattr(reg, "validate_definitions", None)
        if callable(validate_defs):
            validate_defs()

        validate_enum = getattr(reg, "validate_enum_coverage", None)
        if callable(validate_enum):
            validate_enum(strict=True)

    return reg