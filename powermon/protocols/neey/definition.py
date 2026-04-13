from powermon.ports import PortType
from powermon.protocols.crc import crc_pi30
from powermon.protocols.framing import ParenCrcAsciiFrameSpec
from powermon.protocols.model import ProtocolDefinition
from powermon.protocols.types import ProtocolType

from .commands import COMMANDS
from .selectors import SELECTORS

FRAMING = ParenCrcAsciiFrameSpec(crc_func=crc_pi30)

PROTOCOL = ProtocolDefinition(
    protocol_type=ProtocolType.NEEY,
    protocol_id="neey",
    description="NEEY BMS protocol",
    framing=NeeyEncoder(...),
    commands=COMMANDS,
    selectors=SELECTORS,
    supported_ports=frozenset({PortType.SERIAL}),
)
