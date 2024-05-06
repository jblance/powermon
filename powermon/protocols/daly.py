""" protocols / ved.py """
import logging

import construct as cs

from powermon.commands.command import CommandType
from powermon.commands.command_definition import CommandDefinition
from powermon.commands.reading_definition import ReadingType, ResponseType
from powermon.commands.result import ResultType
from powermon.libs.errors import InvalidCRC, InvalidResponse
from powermon.ports.porttype import PortType
from powermon.protocols.abstractprotocol import AbstractProtocol

log = logging.getLogger("daly")

soc_construct = cs.Struct(
    "start_flag" / cs.Bytes(1),
    "module_address" / cs.Bytes(1),
    "command_id" / cs.Bytes(1),
    "data_length" / cs.Byte,
    "battery_voltage" / cs.Int16ub,
    "acquistion_voltage" / cs.Int16ub,
    "current" / cs.Int16ub,
    "soc" / cs.Int16ub,
    "checksum" / cs.Bytes(1)
)

COMMANDS = {
    "SOC": {
        "name": "SOC",
        "description": "State of Charge",
        "help": " -- display the battery state of charge",
        # "type": "DALY",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": "90",
        "result_type": ResultType.CONSTRUCT,
        "construct": soc_construct,
        "construct_min_response": 13,
        "reading_definitions": [
            {"index": "start_flag", "description": "start flag", "reading_type": ReadingType.IGNORE, "response_type": ResponseType.HEX_CHAR},
            {"index": "module_address", "description": "module address", "reading_type": ReadingType.IGNORE, "response_type": ResponseType.HEX_CHAR},
            {"index": "command_id", "description": "command id", "reading_type": ReadingType.IGNORE, "response_type": ResponseType.HEX_CHAR},
            {"index": "data_length", "description": "data length", "reading_type": ReadingType.IGNORE},
            {"index": "battery_voltage", "description": "Battery Bank Voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10"},
            {"index": "acquistion_voltage", "description": "acquistion", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10"},
            {"index": "current", "description": "Current", "reading_type": ReadingType.CURRENT, "response_type": ResponseType.TEMPLATE_INT, "format_template": "(r-30000)/10"},
            {"index": "soc", "description": "SOC", "reading_type": ReadingType.PERCENTAGE, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10"},
            {"index": "checksum", "description": "checksum", "reading_type": ReadingType.IGNORE, "response_type": ResponseType.HEX_CHAR}],
        "test_responses": [
            b"\xa5\x01\x90\x08\x02\x10\x00\x00uo\x03\xbc\xf3",
            b"\xa5\x01\x90\x08\x02\x14\x00\x00uE\x03x\x89",
            b"\xa5\x01\x90\x08\x01\t\x00\x00u\xcf\x03\n\x99",
            b"",
        ],
    },
}


class Daly(AbstractProtocol):
    """
    Daly BMS protocol handler
    """

    def __str__(self):
        return "DALY protocol handler for DALY BMS"

    def __init__(self) -> None:
        super().__init__()
        self.protocol_id = b"DALY"
        self.add_command_definitions(COMMANDS)
        self.add_supported_ports([PortType.SERIAL, PortType.USB])
        self.check_definitions_count(expected=None)

    def get_full_command(self, command) -> bytes:
        """
        Override the default get_full_command
        """
        log.info("Using protocol %s with %i commands", self.protocol_id, len(self.command_definitions))

        command_definition : CommandDefinition = self.get_command_definition(command)
        if command_definition is None:
            return None

        # DALY commands
        #
        #
        # 95 -> a58095080000000000000000c2
        #       a58090080000000000000000bd
        source = 0x80  # 4 = USB, 8 = Bluetooth
        command = command_definition.command_code
        data_length = 8
        full_command = bytearray()
        full_command.append(0xa5)  # start flag
        full_command.append(source)
        full_command.append(bytes.fromhex(command_definition.command_code)[0])
        full_command.append(data_length)
        full_command += bytearray(data_length)
        full_command.append(sum(full_command) & 0xFF)
        full_command.append(10)
        full_command = bytes(full_command)
        log.debug("full_command: %s", full_command)
        return full_command

    def check_valid(self, response: str, command_definition: CommandDefinition = None) -> bool:
        """ check response is valid """
        log.debug("check valid for %s, definition: %s", response, command_definition)
        if response is None:
            raise InvalidResponse("Response is None")
        if len(response) <= 6:
            raise InvalidResponse("Response is too short")
        if response[0] != 0xa5:
            raise InvalidResponse("Response has incorrect start byte")
        if int(response[3]) != len(response[4:-1]):
            raise InvalidResponse("Response length does not match expected")
        return True

    def check_crc(self, response: str, command_definition: CommandDefinition = None) -> bool:
        """ crc check, needs override in protocol """
        log.debug("checking crc for %s", response)
        calc_crc = sum(response[:-1]) & 0xFF
        response_crc = response[-1]

        if response_crc != calc_crc:
            raise InvalidCRC(f"response has invalid CRC - got '\\x{response_crc:02x}', calculated '\\x{calc_crc:02x}")
        # log.debug("Checksum matches in response '%s' response_crc:'%s'", response, calc_crc)
        return True

    def trim_response(self, response: str, command_definition: CommandDefinition = None) -> str:
        """ Remove extra characters from response """
        log.debug("response: %s", response)
        return response
