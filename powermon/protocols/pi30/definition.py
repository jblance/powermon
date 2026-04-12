from powermon.protocols.crc import crc_pi30
from powermon.protocols.framing import ParenCrcAsciiFrameSpec
from powermon.protocols.model import ProtocolDefinition
from powermon.protocols.types import ProtocolType

from .commands import COMMANDS
from .selectors import SELECTORS

PI30_FRAMING = ParenCrcAsciiFrameSpec(crc_func=crc_pi30)

PI30_PROTOCOL = ProtocolDefinition(
    protocol_type=ProtocolType.PI30,
    protocol_id="pi30",
    description="PI30 protocol",
    framing=PI30_FRAMING,
    commands=COMMANDS,
    selectors=SELECTORS,
)
