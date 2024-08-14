""" protocols / neey.py """
import logging

import construct as cs

from powermon.commands.command import CommandType
from powermon.commands.command_definition import CommandDefinition
from powermon.commands.reading_definition import ReadingType, ResponseType
from powermon.commands.result import ResultType
from powermon.libs.errors import InvalidCRC, InvalidResponse, CommandDefinitionIncorrect
from powermon.ports.porttype import PortType
from powermon.protocols.abstractprotocol import AbstractProtocol

log = logging.getLogger("neey")

device_info_construct = cs.Struct(
    "start_flag" / cs.Bytes(2),
    "module_address" / cs.Bytes(1),
    "function" / cs.Bytes(1),
    "command" / cs.Int16ul,
    "length" / cs.Int16ul,
    "model" / cs.Bytes(16),
    "hw_version" / cs.Bytes(8),
    "sw_version" / cs.Bytes(8),
    "protocol_version" / cs.Bytes(8),
    "production_date" / cs.Bytes(8),
    "power_on_count" / cs.Int32ul,
    "total_runtime" / cs.Int32ul,
    "unused" / cs.Bytes(34),
    "crc" / cs.Bytes(1),
    "end_flag" / cs.Bytes(1),
)

cell_info_construct = cs.Struct(
    "start_flag" / cs.Bytes(2),
    "module_address" / cs.Bytes(1),
    "function" / cs.Bytes(1),
    "command" / cs.Int16ul,
    "length" / cs.Int16ul,
 
    "unused" / cs.Bytes(34),
    "crc" / cs.Bytes(1),
    "end_flag" / cs.Bytes(1),
)

COMMANDS = {
    "device_info": {
        "name": "device_info",
        "description": "balancer device information",
        "help": " -- display the balancer info",
        # "type": "DALY",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": "01",
        "result_type": ResultType.CONSTRUCT,
        "construct": device_info_construct,
        "construct_min_response": 100,
        "reading_definitions": [
            {"index": "start_flag", "description": "start flag", "reading_type": ReadingType.HEX_CHARS, "response_type": ResponseType.HEX_CHARS},
            {"index": "module_address", "description": "module address", "reading_type": ReadingType.HEX_STR, "response_type": ResponseType.HEX_CHAR},
            {"index": "function", "description": "function", "reading_type": ReadingType.HEX_STR, "response_type": ResponseType.HEX_CHAR},
            {"index": "command", "description": "command", "reading_type": ReadingType.MESSAGE},
            {"index": "length", "description": "length", "reading_type": ReadingType.MESSAGE},
            {"index": "model", "description": "model", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.BYTES_STRIP_NULLS},
            {"index": "hw_version", "description": "hw_version", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.BYTES_STRIP_NULLS},
            {"index": "sw_version", "description": "sw_version", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.BYTES_STRIP_NULLS},
            {"index": "protocol_version", "description": "protocol_version", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.BYTES_STRIP_NULLS},
            {"index": "production_date", "description": "production_date", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.BYTES_STRIP_NULLS},
            {"index": "power_on_count", "description": "power_on_count", "reading_type": ReadingType.MESSAGE},
            {"index": "total_runtime", "description": "total_runtime", "reading_type": ReadingType.TIME_SECONDS},
            {"index": "crc", "description": "crc", "reading_type": ReadingType.HEX_STR, "response_type": ResponseType.HEX_CHAR},
            {"index": "end_flag", "description": "end flag", "reading_type": ReadingType.HEX_STR, "response_type": ResponseType.HEX_CHAR},
        ],
        "test_responses": [
            b'U\xaa\x11\x01\x01\x00d\x00GW-24S4EB\x00\x00\x00\x00\x00\x00\x00HW-2.8.0ZH-1.2.3V1.0.0\x00\x0020220916\x04\x00\x00\x00n\x85?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00G\xff'
        ],
    },
    "cell_info": {
        "name": "cell_info",
        "description": "information about the cells",
        "help": " -- display the cell info",
        # "type": "DALY",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": "02",
        "result_type": ResultType.CONSTRUCT,
        "construct": cell_info_construct,
        "construct_min_response": 300,
        "reading_definitions": [
            {"index": "start_flag", "description": "start flag", "reading_type": ReadingType.HEX_CHARS, "response_type": ResponseType.HEX_CHARS},
            {"index": "module_address", "description": "module address", "reading_type": ReadingType.HEX_STR, "response_type": ResponseType.HEX_CHAR},
            {"index": "function", "description": "function", "reading_type": ReadingType.HEX_STR, "response_type": ResponseType.HEX_CHAR},
            {"index": "command", "description": "command", "reading_type": ReadingType.MESSAGE},
            {"index": "length", "description": "length", "reading_type": ReadingType.MESSAGE},
           
        ],
        "test_responses": [
            b'U\xaa\x11\x01\x01\x00d\x00GW-24S4EB\x00\x00\x00\x00\x00\x00\x00HW-2.8.0ZH-1.2.3V1.0.0\x00\x0020220916\x04\x00\x00\x00n\x85?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00G\xff'
        ],
    },
}

# static const uint8_t SOF_REQUEST_BYTE1 = 0xAA;
# static const uint8_t SOF_REQUEST_BYTE2 = 0x55;
# static const uint8_t SOF_RESPONSE_BYTE1 = 0x55;
# static const uint8_t SOF_RESPONSE_BYTE2 = 0xAA;
# static const uint8_t DEVICE_ADDRESS = 0x11;

# static const uint8_t FUNCTION_WRITE = 0x00;
# static const uint8_t FUNCTION_READ = 0x01;

# static const uint8_t COMMAND_NONE = 0x00;
# static const uint8_t COMMAND_DEVICE_INFO = 0x01;
# static const uint8_t COMMAND_CELL_INFO = 0x02;
# static const uint8_t COMMAND_FACTORY_DEFAULTS = 0x03;
# static const uint8_t COMMAND_SETTINGS = 0x04;
# static const uint8_t COMMAND_WRITE_REGISTER = 0x05;

# static const uint8_t END_OF_FRAME = 0xFF;

#   // Request device info:
#   // 0xAA 0x55 0x11 0x01 0x01 0x00 0x14 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0xFA 0xFF
#   //
#   // Request cell info:
#   // 0xAA 0x55 0x11 0x01 0x02 0x00 0x00 0x14 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0xF9 0xFF
#   //
#   // Request factory settings:
#   // 0xAA 0x55 0x11 0x01 0x03 0x00 0x14 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0xF8 0xFF
#   //
#   // Request settings:
#   // 0xAA 0x55 0x11 0x01 0x04 0x00 0x14 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0xFF 0xFF
#   //
#   // Enable balancer:
#   // 0xAA 0x55 0x11 0x00 0x05 0x0D 0x14 0x00 0x01 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0xF3 0xFF
#   //
#   // Disable balancer:
#   // 0xAA 0x55 0x11 0x00 0x05 0x0D 0x14 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0xF2 0xFF


class Neey(AbstractProtocol):
    """
    Neey Active Balancer rotocol handler
    """

    def __str__(self):
        return "NEEY protocol handler for NEEY balanceer"

    def __init__(self) -> None:
        super().__init__()
        self.protocol_id = b"NEEY"
        self.add_command_definitions(COMMANDS)
        self.add_supported_ports([PortType.BLE])
        self.notifier_handle = 9
        self.intializing_handle = 0
        self.command_handle = 15
        self.check_definitions_count(expected=None)

        # bytes.fromhex('aa5511 010100140000000000000000000000faff')

    def get_full_command(self, command: bytes|str) -> bytes:
        # test_command = bytes.fromhex('aa5511010100140000000000000000000000faff')
        # test_command = bytes.fromhex('aa5511010200001400000000000000000000f9ff')
        log.info("Using protocol %s with %i commands", self.protocol_id, len(self.command_definitions))

        command_definition : CommandDefinition = self.get_command_definition(command)
        if command_definition is None:
            return None

        # fix a 'bug' that seems to be implemented on the device?
        if command_definition.code == "device_info":
            data_length = cs.Int16ul.build(20)
        else:
            data_length = cs.Int16ub.build(20)
        command_bytes = cs.Int16ul.build(int(command_definition.command_code))

        full_command = bytearray(20)
        full_command[0] = 0xaa  # start flag
        full_command[1] = 0x55  # start flag
        full_command[2] = 0x11  # module address
        full_command[3] = 0x01  # function
        full_command[4] = command_bytes[0]  # command code
        full_command[5] = command_bytes[1]  # command code
        full_command[6] = data_length[0]  # length
        full_command[7] = data_length[1]  # length
        checksum = self.checksum(full_command)
        full_command[-2] = checksum
        full_command[-1] = 0xff
        # print(test_command)
        # print(bytes(full_command))
        # print(test_command == bytes(full_command))
        return bytes(full_command)

    def check_valid(self, response: str, command_definition: CommandDefinition = None) -> bool:
        """check if the response is valid

        Args:
            response (str): the response to check
            command_definition (CommandDefinition, optional): not used in the check for this protocol. Defaults to None.

        Raises:
            InvalidResponse: exception raised if the response is invalid for any reason

        Returns:
            bool: True if response doesnt meet any 'invalid' tests
        """
        log.debug("check valid for %s, definition: %s", response, command_definition)
        if response is None:
            raise InvalidResponse("Response is None")
        if len(response) <= 6:
            raise InvalidResponse("Response is too short")
        if response[0] != 0x55:
            raise InvalidResponse("Response has incorrect start byte")
        if int(response[-1]) != 0xff:
            raise InvalidResponse("Response has incorrect end byte")
        return True

    def checksum(self, response):
        calc_crc = 0 
        for i in response:
            calc_crc = calc_crc ^ i
        return calc_crc

    def crc(self, response):
        return sum(response) & 0xFF

    def check_crc(self, response: str, command_definition: CommandDefinition = None) -> bool:
        """ crc check, needs override in protocol """
        log.debug("checking crc for %s", response)
        if response.count(b'\xa5') > 1:
            # multiframe response - crch calc incorrect
            return True
        calc_crc = self.crc(response[:-2])
        response_crc = response[-2]

        if response_crc != calc_crc:
            raise InvalidCRC(f"response has invalid CRC - got '\\x{response_crc:02x}', calculated '\\x{calc_crc:02x}")
        # log.debug("Checksum matches in response '%s' response_crc:'%s'", response, calc_crc)
        return True

    def trim_response(self, response: str, command_definition: CommandDefinition = None) -> str:
        """ Remove extra characters from response """
        log.debug("response: %s", response)
        return response
