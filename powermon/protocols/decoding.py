from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence

from powermon.protocols.model import ParsedResponse, ReadingDefinition

# Import transforms for typing (not required at runtime if you use Protocols)
# from powermon.protocols.transforms import Transform

_INDEX_RE = re.compile(r"^(?P<name>[A-Za-z_][A-Za-z0-9_]*)\[(?P<idx>\d+)\]$")


class DecodeError(Exception):
    """Base error for decoding failures."""


class PathError(DecodeError):
    """Raised when resolving a path fails."""


class FieldError(DecodeError):
    """Raised when extracting a field by index fails."""


def get_path(data: Any, path: str) -> Any:
    """
    Resolve dotted paths with optional [index] components against dict/Container/list.

    Examples:
      "battery_voltage_10mV"
      "cell_array[0].cell_voltage_mV"
      "settings.buzzer_mode"
    """
    cur = data
    for part in path.split("."):
        m = _INDEX_RE.match(part)
        if m:
            name = m.group("name")
            idx = int(m.group("idx"))
            cur = _get_key(cur, name)
            try:
                cur = cur[idx]
            except Exception as exc:
                raise PathError(f"Index [{idx}] not valid for '{name}' in path '{path}'") from exc
        else:
            cur = _get_key(cur, part)
    return cur


def _get_key(obj: Any, key: str) -> Any:
    if isinstance(obj, Mapping):
        try:
            return obj[key]
        except KeyError as exc:
            raise PathError(f"Key '{key}' not found") from exc
    # construct.Container often supports attribute access
    try:
        return getattr(obj, key)
    except AttributeError as exc:
        raise PathError(f"Attribute '{key}' not found") from exc


def _is_missing(value: Any, missing: set[str]) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in missing
    return False


def _coerce_scalar(value: Any, rd: ReadingDefinition) -> Any:
    """
    Convert a scalar token into rd.dtype.

    This handles the fact that PI30 emits strings, while construct-based parsers
    may emit ints/floats already.
    """
    dtype = getattr(rd, "dtype", str)
    base = getattr(rd, "base", None)  # optional attribute (safe if not present)
    strip = getattr(rd, "strip", True)

    # Already correct type?
    if dtype is not Any and isinstance(value, dtype):
        return value

    # Strings: common for PI30
    if isinstance(value, str):
        s = value.strip() if strip else value

        if dtype is str:
            return s

        if dtype is bool:
            sl = s.lower()
            if sl in ("1", "true", "t", "yes", "y", "on", "enabled"):
                return True
            if sl in ("0", "false", "f", "no", "n", "off", "disabled"):
                return False
            return bool(int(s, base or 10))

        if dtype is int:
            return int(s, base or 10)

        if dtype is float:
            if s == "":
                raise DecodeError("empty float field")
            return float(s)

        # fallback: try constructor
        return dtype(s)

    # Bytes -> str only if requested
    if isinstance(value, (bytes, bytearray)) and dtype is str:
        return bytes(value).decode("ascii", errors="replace")

    # Fallback: attempt dtype constructor (covers int->float etc.)
    try:
        return dtype(value)
    except Exception as exc:
        raise DecodeError(f"Failed to coerce {value!r} ({type(value).__name__}) to {dtype}") from exc


def extract_raw(parsed: ParsedResponse, rd: ReadingDefinition) -> Any:
    """
    Extract the raw token for a reading.

    Supports:
      - rd.path with parsed.data (construct/dict)
      - rd.index with parsed.fields (PI30 token lists)

    This is intentionally forgiving so you can migrate incrementally.
    """
    path = getattr(rd, "path", None)
    index = getattr(rd, "index", None)

    if path is not None:
        data = getattr(parsed, "data", None)
        if data is None:
            raise PathError(f"Reading '{rd.label}' uses path '{path}' but ParsedResponse.data is None")
        return get_path(data, path)

    if index is None:
        raise DecodeError(f"Reading '{rd.label}' must specify either path or index")

    fields = getattr(parsed, "fields", None)
    if fields is None:
        raise FieldError(f"ParsedResponse.fields is None but index={index} requested")

    try:
        return fields[index]
    except Exception as exc:
        if getattr(rd, "optional", False):
            return None
        raise FieldError(
            f"Reading '{rd.label}' index {index} out of range (fields={len(fields)})"
        ) from exc


def decode_reading(parsed: ParsedResponse, rd: ReadingDefinition) -> Any:
    """
    Extract + coerce + transform a single reading.
    """
    # Missing policy (optional). Defaults to common placeholders.
    missing_values = getattr(rd, "missing_values", None)
    if missing_values is None:
        missing = {"", "na", "n/a", "---", "null", "none"}
    else:
        missing = {str(x).strip().lower() for x in missing_values}

    raw = extract_raw(parsed, rd)

    if _is_missing(raw, missing):
        # Decide policy: None is usually best for missing values.
        return None

    coerced = _coerce_scalar(raw, rd)

    transform = getattr(rd, "transform", None)
    if transform is not None:
        try:
            out = transform.apply(coerced)
        except Exception as exc:
            desc = transform.describe() if hasattr(transform, "describe") else type(transform).__name__
            raise DecodeError(f"Transform '{desc}' failed for reading '{rd.label}' value={coerced!r}") from exc

        # Keep numeric dtype consistent if requested
        dtype = getattr(rd, "dtype", None)
        if dtype in (int, float) and out is not None:
            try:
                return dtype(out)
            except Exception as exc:
                raise DecodeError(f"Failed to cast transformed value {out!r} to {dtype} for '{rd.label}'") from exc
        return out

    return coerced


def decode_all(
    parsed: ParsedResponse,
    readings: Mapping[str, ReadingDefinition],
) -> dict[str, Any]:
    """
    Decode all readings for a command. Returns {reading_key: value}.
    """
    out: dict[str, Any] = {}
    for key, rd in readings.items():
        out[key] = decode_reading(parsed, rd)
    return out