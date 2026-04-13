from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, Protocol, Sequence


class Transform(Protocol):
    """
    Declarative transform applied to a decoded value.

    Transforms are intentionally *safe* and do not evaluate arbitrary expressions.
    """

    def apply(self, value: Any) -> Any:
        """Transform a value into another value."""
        ...

    def describe(self) -> str:
        """Human-friendly description used by CLI/docs."""
        ...


def _to_float(value: Any) -> float:
    # Central place to control numeric coercion.
    # Most protocols emit ints/strings; float() is appropriate here.
    return float(value)


@dataclass(frozen=True)
class Identity:
    """No-op transform."""
    def apply(self, value: Any) -> Any:
        return value

    def describe(self) -> str:
        return "identity"


@dataclass(frozen=True)
class Scale:
    """y = x * factor"""
    factor: float

    def apply(self, value: Any) -> Any:
        return _to_float(value) * self.factor

    def describe(self) -> str:
        return f"*{self.factor}"


@dataclass(frozen=True)
class Offset:
    """y = x + offset"""
    offset: float

    def apply(self, value: Any) -> Any:
        return _to_float(value) + self.offset

    def describe(self) -> str:
        sign = "+" if self.offset >= 0 else ""
        return f"x{sign}{self.offset}"


@dataclass(frozen=True)
class Affine:
    """
    Affine transform: y = (x + offset) * factor

    This neatly covers:
      - mV -> V:          offset=0,      factor=0.001
      - (x-30000)/10:     offset=-30000,  factor=0.1
    """
    offset: float = 0.0
    factor: float = 1.0

    def apply(self, value: Any) -> Any:
        return (_to_float(value) + self.offset) * self.factor

    def describe(self) -> str:
        sign = "+" if self.offset >= 0 else ""
        return f"(x{sign}{self.offset})*{self.factor}"


@dataclass(frozen=True)
class Clamp:
    """Clamp numeric values to [min, max] (either bound may be None)."""
    min: float | None = None
    max: float | None = None

    def apply(self, value: Any) -> Any:
        v = _to_float(value)
        if self.min is not None and v < self.min:
            v = self.min
        if self.max is not None and v > self.max:
            v = self.max
        return v

    def describe(self) -> str:
        return f"clamp({self.min},{self.max})"


@dataclass(frozen=True)
class Lookup:
    """
    Map integer-ish codes to values (strings/enums/etc).

    Example:
      Lookup({0: "idle", 1: "charge"}, default="unknown")
    """
    mapping: Mapping[int, Any]
    default: Any = "unknown"

    def apply(self, value: Any) -> Any:
        return self.mapping.get(int(value), self.default)

    def describe(self) -> str:
        return "lookup"


@dataclass(frozen=True)
class BitFlag:
    """Extract a boolean flag from an integer bitfield."""
    bit: int

    def apply(self, value: Any) -> bool:
        return bool(int(value) & (1 << self.bit))

    def describe(self) -> str:
        return f"bit{self.bit}"


@dataclass(frozen=True)
class ExtractKey:
    """
    Extract a key/attribute from mapping/container objects.

    Useful with construct arrays:
      path="cell_array" + ExtractKey("cell_voltage_mV") -> list[int]
    """
    key: str

    def apply(self, value: Any) -> Any:
        # Mapping/construct.Container
        if isinstance(value, Mapping):
            return value[self.key]
        return getattr(value, self.key)

    def describe(self) -> str:
        return f"extract({self.key})"


@dataclass(frozen=True)
class MapEach:
    """Apply a transform to each element of a sequence."""
    transform: Transform

    def apply(self, value: Any) -> Any:
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
            raise TypeError(f"MapEach expected a sequence, got {type(value)!r}")
        return [self.transform.apply(v) for v in value]

    def describe(self) -> str:
        return f"map({self.transform.describe()})"


@dataclass(frozen=True)
class Reduce:
    """
    Reduce a sequence of numeric values to a single value.

    Example:
      Reduce(min, name="min")
      Reduce(max, name="max")
    """
    fn: Callable[[Iterable[float]], float]
    name: str

    def apply(self, value: Any) -> Any:
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
            raise TypeError(f"Reduce expected a sequence, got {type(value)!r}")
        nums = [_to_float(v) for v in value]
        return self.fn(nums)

    def describe(self) -> str:
        return self.name


@dataclass(frozen=True)
class Compose:
    """Apply transforms in order: tN(...t2(t1(x)))"""
    transforms: tuple[Transform, ...]

    def apply(self, value: Any) -> Any:
        out = value
        for t in self.transforms:
            out = t.apply(out)
        return out

    def describe(self) -> str:
        return " -> ".join(t.describe() for t in self.transforms)


@dataclass(frozen=True)
class Func:
    """
    Escape hatch for unusual transforms.

    Keep this internal (not user-provided config) to remain safe.
    """
    fn: Callable[[Any], Any]
    name: str = "func"

    def apply(self, value: Any) -> Any:
        return self.fn(value)

    def describe(self) -> str:
        return self.name
