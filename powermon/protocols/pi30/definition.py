from powermon.ports import PortType
from powermon.protocols.crc import crc_pi30
from powermon.protocols.framing import ParenCrcAsciiFrameSpec
from powermon.protocols.model import ProtocolDefinition
from powermon.protocols.types import ProtocolType

#from .commands.accumulator import WRITE_COMMANDS
from .commands.configread import READ_COMMANDS
from .commands.configwrite import WRITE_COMMANDS
from .commands.identity import ID_COMMANDS
from .commands.metric import METRIC_COMMANDS
from .commands.status import STATUS_COMMANDS
from .selectors import SELECTORS

FRAMING = ParenCrcAsciiFrameSpec(crc_func=crc_pi30)

PROTOCOL = ProtocolDefinition(
    protocol_type=ProtocolType.PI30,
    protocol_id="pi30",
    description="PI30 protocol",
    framing=FRAMING,
    commands=READ_COMMANDS | WRITE_COMMANDS | ID_COMMANDS | METRIC_COMMANDS | STATUS_COMMANDS,
    selectors=SELECTORS,
    supported_ports=frozenset({PortType.SERIAL, PortType.USB}),
)
