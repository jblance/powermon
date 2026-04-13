"""
Core protocol data models.

This module defines *pure*, declarative data structures used by
protocol definitions. There is **no runtime I/O**, **no scheduling**
and **no port logic** here.

These models are shared by:
  - protocol command definitions
  - selector resolution
  - test fixtures / mock ports
  - protocol registries
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Callable, FrozenSet, Mapping, Optional

from powermon.ports import PortType

from .types import ProtocolType

if TYPE_CHECKING:
    from powermon.protocols.transforms import Transform

# ============================================================================
# Command categorisation
# ============================================================================

class CommandCategory(StrEnum):
    IDENTITY     = "identity"      # serial, model, firmware
    METRIC       = "metric"        # fast telemetry
    ACCUMULATOR  = "accumulator"   # counters / energy totals
    STATUS       = "status"        # health, modes, warnings
    CONFIG_READ  = "config_read"
    CONFIG_WRITE = "config_write"


# ============================================================================
# Request / response structure
# ============================================================================

@dataclass(frozen=True)
class RequestSpec:
    """
    Declarative request definition.

    Describes *what* bytes are sent, not *how* they are sent.
    """
    command: str
    terminator: bytes = b"\r"
    crc: bool = True

    def build(
        self,
        *,
        crc_func: Callable[[bytes], bytes],
        payload: Optional[str] = None,
    ) -> bytes:
        body = self.command + (payload or "")
        raw = body.encode("ascii")
        if self.crc:
            raw += crc_func(raw)
        return raw + self.terminator

@dataclass(frozen=True)
class ParsedResponse:
    """
    Result of protocol-level parsing *before* decoding readings.
    """
    raw: bytes
    fields: list[str]
    data: Optional[Mapping[str, Any]] = None  # construct.Container / dict for binary protocols


@dataclass(frozen=True)
class ResponseSpec:
    """
    Describes how to parse a response payload.

    Validation (framing, CRC) happens *before* this stage.
    """
    parser: Callable[[bytes], ParsedResponse]
    crc: bool = True
    min_fields: Optional[int] = None
    max_fields: Optional[int] = None

    def parse(
        self,
        payload: bytes,
        *,
        crc_func: Callable[[bytes], bytes] | None = None,
    ) -> ParsedResponse:
        # CRC is normally handled by FrameSpec; keep this hook minimal
        parsed = self.parser(payload)

        if self.min_fields is not None and len(parsed.fields) < self.min_fields:
            raise ValueError("Too few response fields")
        if self.max_fields is not None and len(parsed.fields) > self.max_fields:
            raise ValueError("Too many response fields")

        return parsed


# ============================================================================
# Readings and parameters
# ============================================================================

@dataclass(frozen=True)
class ReadingDefinition:
    """
    Definition of a single decoded value within a response.

    Exactly one of `index` or `path` should be set:
      - index: extract from ParsedResponse.fields (PI30-style token lists)
      - path:  extract from ParsedResponse.data (construct Container / dict)
    """
    label: str
    unit: str
    dtype: type                    # e.g. int, float, bool, str
    description: str = ""

    index: Optional[int] = None
    path: Optional[str] = None

    transform: Optional["Transform"] = None

    # Optional: decoding hints for string fields (useful for PI30)
    base: Optional[int] = None     # e.g. 16 for hex string fields
    strip: bool = True

    # Optional: treat these values as "missing" -> return None
    missing_values: Optional[set[str]] = None
    optional: bool = False


@dataclass(frozen=True)
class ParameterSpec:
    """
    Definition of a parameter accepted by a command.
    """
    name: str
    pattern: object               # typically a compiled regex
    description: str

    def validate(self, value: str):
        # pattern is intentionally opaque (regex, callable, etc.)
        if hasattr(self.pattern, "fullmatch"):
            if not self.pattern.fullmatch(value):
                raise ValueError(f"Invalid value for {self.name}: {value}")
        elif callable(self.pattern):
            if not self.pattern(value):
                raise ValueError(f"Invalid value for {self.name}: {value}")


# ============================================================================
# Command definition (core semantic unit)
# ============================================================================

@dataclass(frozen=True)
class CommandDefinition:
    """
    Declarative description of a protocol command.

    CommandDefinition:
      - does NOT execute anything
      - does NOT schedule anything
      - does NOT own runtime state
    """
    command_id: str                         # canonical protocol command (e.g. "QPIGS")
    name: str                      # human label
    description: str

    request: RequestSpec
    response: ResponseSpec

    readings: Mapping[str, ReadingDefinition] = field(default_factory=dict)
    parameters: Mapping[str, ParameterSpec] = field(default_factory=dict)

    category: CommandCategory = CommandCategory.STATUS
    side_effects: bool = False      # true for config-write commands


# ============================================================================
# Human-facing selector resolution
# ============================================================================

@dataclass(frozen=True)
class SelectorTarget:
    """
    Maps a human-friendly token to protocol semantics.

    Exactly ONE of `reading_key` or `parameter` may be set.
    """
    command_id: str
    reading_key: Optional[str] = None   # extract a single reading
    parameter: Optional[str] = None     # write parameter


# ============================================================================
# Test / simulation fixtures (deliberately non-authoritative)
# ============================================================================

@dataclass(frozen=True)
class CommandFixture:
    """
    Non-authoritative sample response captured from real devices.

    Used for:
      - mock ports
      - regression tests
      - protocol parser validation
    """
    description: str
    raw_response: bytes
    notes: Optional[str] = None


# ============================================================================
# Protocol definition (binding glue)
# ============================================================================

@dataclass(frozen=True)
class ProtocolDefinition:
    """
    Binds protocol-wide components together.

    This is declarative only; runtime owns execution.
    """
    protocol_type: ProtocolType     # ProtocolType enum
    protocol_id: str                # wire / descriptive identifier ("PI30")
    description: str

    framing: object                 # FrameSpec (defined in framing.py)
    commands: Mapping[str, CommandDefinition]
    selectors: Mapping[str, SelectorTarget]

    supported_ports: FrozenSet[PortType] = field(default_factory=frozenset)
