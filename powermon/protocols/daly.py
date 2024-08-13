""" protocols / daly.py """
# much of the deocde info from https://github.com/dreadnought/python-daly-bms/blob/main/dalybms/daly_bms.py
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

cvr_construct = cs.Struct(
    "start_flag" / cs.Bytes(1),
    "module_address" / cs.Bytes(1),
    "command_id" / cs.Bytes(1),
    "data_length" / cs.Byte,
    "highest_voltage" / cs.Int16ub,
    "highest_cell" / cs.Byte,
    "lowest_voltage" / cs.Int16ub,
    "lowest_cell" / cs.Byte,
    "rest" / cs.Bytes(2),
    "checksum" / cs.Bytes(1)
)

temps_construct = cs.Struct(
    "start_flag" / cs.Bytes(1),
    "module_address" / cs.Bytes(1),
    "command_id" / cs.Bytes(1),
    "data_length" / cs.Byte,
    "highest_temperature" / cs.Byte,
    "highest_sensor" / cs.Byte,
    "lowest_temperature" / cs.Byte,
    "lowest_sensor" / cs.Byte,
    "rest" / cs.Bytes(4),
    "checksum" / cs.Bytes(1)
)

mos_construct = cs.Struct(
    "start_flag" / cs.Bytes(1),
    "module_address" / cs.Bytes(1),
    "command_id" / cs.Bytes(1),
    "data_length" / cs.Byte,
    "mode" / cs.Enum(cs.Int8sb, stationary=0, charging=1, discharging=2),
    "charging_mosfet" / cs.Byte,
    "discharging_mosfet" / cs.Byte,
    "bms_cycles" / cs.Int8ub,
    "capacity_ah" / cs.Int32ub,
    "checksum" / cs.Bytes(1)
)

status_construct = cs.Struct(
    "start_flag" / cs.Bytes(1),
    "module_address" / cs.Bytes(1),
    "command_id" / cs.Bytes(1),
    "data_length" / cs.Byte,
    "mode" / cs.Enum(cs.Int8sb, stationary=0, charging=1, discharging=2),
    "charging_mosfet" / cs.Byte,
    "discharging_mosfet" / cs.Byte,
    "bms_cycles" / cs.Int8ub,
    "capacity_ah" / cs.Int32ub,
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
            b'\xa5\x01\x90\x08\x02\x0c\x00\x00u>\x00\r\x0c',
        ],
    },
    "cell_voltage_range": {
        "name": "cell_voltage_range",
        "description": "cell_voltage_range",
        "help": " -- display the battery cell_voltage_range",
        # "type": "DALY",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": "91",
        "result_type": ResultType.CONSTRUCT,
        "construct": cvr_construct,
        "construct_min_response": 13,
        "reading_definitions": [
            {"index": "start_flag", "description": "start flag", "reading_type": ReadingType.IGNORE, "response_type": ResponseType.HEX_CHAR},
            {"index": "module_address", "description": "module address", "reading_type": ReadingType.IGNORE, "response_type": ResponseType.HEX_CHAR},
            {"index": "command_id", "description": "command id", "reading_type": ReadingType.IGNORE, "response_type": ResponseType.HEX_CHAR},
            {"index": "data_length", "description": "data length", "reading_type": ReadingType.IGNORE},
            {"index": "highest_voltage", "description": "highest_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "highest_cell", "description": "highest_cell", "reading_type": ReadingType.NUMBER},
            {"index": "lowest_voltage", "description": "lowest_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "lowest_cell", "description": "lowest_cell", "reading_type": ReadingType.NUMBER},
        ],
        "test_responses": [
            b'\xa5\x01\x91\x08\x0c\xfc\x07\x0c\xe3\x01\x03\xc7\x08',
        ],
    },
    "temperatures": {
        "name": "temperatures",
        "description": "temperatures",
        "help": " -- display the battery temperatures",
        # "type": "DALY",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": "92",
        "result_type": ResultType.CONSTRUCT,
        "construct": temps_construct,
        "construct_min_response": 13,
        "reading_definitions": [
            {"index": "start_flag", "description": "start flag", "reading_type": ReadingType.IGNORE, "response_type": ResponseType.HEX_CHAR},
            {"index": "module_address", "description": "module address", "reading_type": ReadingType.IGNORE, "response_type": ResponseType.HEX_CHAR},
            {"index": "command_id", "description": "command id", "reading_type": ReadingType.IGNORE, "response_type": ResponseType.HEX_CHAR},
            {"index": "data_length", "description": "data length", "reading_type": ReadingType.IGNORE},
            {"index": "highest_temperature", "description": "highest_temperature", "reading_type": ReadingType.TEMPERATURE, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r-40"},
            {"index": "highest_sensor", "description": "highest_sensor", "reading_type": ReadingType.NUMBER},
            {"index": "lowest_temperature", "description": "lowest_temperature", "reading_type": ReadingType.TEMPERATURE, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r-40"},
            {"index": "lowest_sensor", "description": "lowest_sensor", "reading_type": ReadingType.NUMBER},
        ],
        "test_responses": [
            b'\xa5\x01\x92\x08.\x01.\x01\x8c\x07\x03\xc5\xf9',
        ],
    },
    "mosfet": {
        "name": "mosfet",
        "description": "mosfet",
        "help": " -- display the battery mosfet",
        # "type": "DALY",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": "93",
        "result_type": ResultType.CONSTRUCT,
        "construct": mos_construct,
        "construct_min_response": 13,
        # "result_type": ResultType.SINGLE,
        # "reading_definitions": [{"reading_type": ReadingType.MESSAGE, "description": "General Model Number", "response_type": ResponseType.BYTES}],
        "reading_definitions": [
            {"index": "start_flag", "description": "start flag", "reading_type": ReadingType.IGNORE, "response_type": ResponseType.HEX_CHAR},
            {"index": "module_address", "description": "module address", "reading_type": ReadingType.IGNORE, "response_type": ResponseType.HEX_CHAR},
            {"index": "command_id", "description": "command id", "reading_type": ReadingType.IGNORE, "response_type": ResponseType.HEX_CHAR},
            {"index": "data_length", "description": "data length", "reading_type": ReadingType.IGNORE},
            {"index": "mode", "description": "mode", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "charging_mosfet", "description": "charging_mosfet", "reading_type": ReadingType.ENABLED, "response_type": ResponseType.BOOL},
            {"index": "discharging_mosfet", "description": "discharging_mosfet", "reading_type": ReadingType.ENABLED, "response_type": ResponseType.BOOL},
            {"index": "bms_cycles", "description": "bms_cycles", "reading_type": ReadingType.NUMBER},
            {"index": "capacity_ah", "description": "capacity_ah", "reading_type": ReadingType.ENERGY, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
        ],
        "test_responses": [
            b'\xa5\x01\x93\x08\x02\x01\x01\x97\x00\x04-\xfa\x07'
        ],
    },
    "status": {
        "name": "status",
        "description": "status",
        "help": " -- display the battery status",
        # "type": "DALY",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": "94",
        "result_type": ResultType.CONSTRUCT,
        "construct": status_construct,
        "construct_min_response": 13,
        # "result_type": ResultType.SINGLE,
        # "reading_definitions": [{"reading_type": ReadingType.MESSAGE, "description": "General Model Number", "response_type": ResponseType.BYTES}],
        "reading_definitions": [
            {"index": "start_flag", "description": "start flag", "reading_type": ReadingType.IGNORE, "response_type": ResponseType.HEX_CHAR},
            {"index": "module_address", "description": "module address", "reading_type": ReadingType.IGNORE, "response_type": ResponseType.HEX_CHAR},
            {"index": "command_id", "description": "command id", "reading_type": ReadingType.IGNORE, "response_type": ResponseType.HEX_CHAR},
            {"index": "data_length", "description": "data length", "reading_type": ReadingType.IGNORE},
            {"index": "mode", "description": "mode", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "charging_mosfet", "description": "charging_mosfet", "reading_type": ReadingType.ENABLED, "response_type": ResponseType.BOOL},
            {"index": "discharging_mosfet", "description": "discharging_mosfet", "reading_type": ReadingType.ENABLED, "response_type": ResponseType.BOOL},
            {"index": "bms_cycles", "description": "bms_cycles", "reading_type": ReadingType.NUMBER},
            {"index": "capacity_ah", "description": "capacity_ah", "reading_type": ReadingType.ENERGY, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
        ],
        "test_responses": [
            b'\xa5\x01\x93\x08\x02\x01\x01\x97\x00\x04-\xfa\x07'
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
        self.add_supported_ports([PortType.SERIAL, PortType.USB, PortType.BLE])
        self.notifier_handle = 17
        self.intializing_handle = 48
        self.command_handle = 15
        self.check_definitions_count(expected=None)

    def get_full_command(self, command: bytes|str) -> bytes:
        """generate the full command for a Daly device from a supplied command name

        Args:
            command (bytes | str): the command name - references the COMMANDS dict key

        Returns:
            bytes: full command with start flag, source, command code, data length and checksum
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
        if self.port_type == PortType.BLE:
            source = 0x80  # 4 = USB, 8 = Bluetooth
        else:
            source = 0x40
        command = command_definition.command_code
        data_length = 8
        full_command = bytearray()

        full_command.append(0xa5)  # start flag
        full_command.append(source)  # source code
        full_command.append(bytes.fromhex(command_definition.command_code)[0])  # command code
        full_command.append(data_length)  # data length
        full_command += bytearray(data_length)  # pad to correct length
        full_command.append(sum(full_command) & 0xFF)  # append checksum
        if self.port_type is not PortType.BLE:
            full_command.append(10)  # append newline except for BLE commands
        full_command = bytes(full_command)
        log.debug("full_command: %s", full_command)
        return full_command

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
