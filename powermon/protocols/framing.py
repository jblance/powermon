from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable, Mapping, Any

from powermon.exceptions import InvalidCRC, InvalidResponse
from powermon.protocols.model import CommandDefinition
from powermon.ports._types import PortType


@dataclass(frozen=True)
class EncodeContext:
    port_type: PortType
    # optional future fields: address, baud, mtu, etc.


@runtime_checkable
class FrameSpec(Protocol):
    """Reusable framing/validation rules for a protocol transport."""

    def encode_request(self, cmd: CommandDefinition, *, params: Mapping[str, Any] | None, ctx: EncodeContext) -> bytes:
        """ """

    def validate_response(self, data: bytes, *, ctx: EncodeContext) -> bytes: 
        """ optional; returns payload/unframed bytes """


    def validate(self, frame: bytes) -> None:
        """Raise InvalidResponse if the raw frame is invalid."""

    def verify_crc(self, frame: bytes) -> None:
        """Raise InvalidCRC if CRC mismatch; no-op for specs without CRC."""

    def strip(self, frame: bytes) -> bytes:
        """
        Return the payload bytes (what parsers should see), excluding framing/CRC/terminator.
        """
        ...


@dataclass(frozen=True)
class ParenCrcAsciiFrameSpec:
    """
    Framing for PI30-style protocols:
      - Response starts with '('
      - Ends with <crc_hi><crc_lo> + '\\r'
      - CRC computed over bytes before CRC (typically includes '(')
    """

    start: bytes = b"("
    terminator: bytes = b"\r"

    # Inject the CRC function so the same FrameSpec can be reused elsewhere if needed
    crc_func: callable = None  # type: ignore[assignment]

    def validate(self, frame: bytes) -> None:
        if frame is None:
            raise InvalidResponse("Response is None")
        if len(frame) <= 3:
            raise InvalidResponse("Response is too short")
        if not frame.startswith(self.start):
            raise InvalidResponse("Response missing start character '('")
        if not frame.endswith(self.terminator):
            raise InvalidResponse("Response missing terminator '\\r'")

    def verify_crc(self, frame: bytes) -> None:
        if self.crc_func is None:
            raise RuntimeError("crc_func is not configured for this FrameSpec")

        # Frame layout: b"(...payload...<crc_hi><crc_lo>\\r"
        payload = frame[:-3]     # everything except crc_hi crc_lo \r
        recv_crc = frame[-3:-1]  # crc_hi crc_lo
        calc_crc = self.crc_func(payload)

        if recv_crc != calc_crc:
            raise InvalidCRC(f"CRC mismatch: got {recv_crc!r}, expected {calc_crc!r}")

    def strip(self, frame: bytes) -> bytes:
        # return payload excluding '(' and excluding CRC+CR
        # frame: b"(<payload><crc2>\\r"
        return frame[1:-3]