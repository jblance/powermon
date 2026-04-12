""" protocols / daly.py """
# much of the deocde info from https://github.com/dreadnought/python-daly-bms/blob/main/dalybms/daly_bms.py
import logging

import construct as cs

from powermon.commands.command import CommandType
from powermon.commands.command_definition import CommandDefinition
from powermon.commands.reading_definition import ReadingType, ResponseType
from powermon.commands.result import ResultType
from powermon.libs.errors import (CommandDefinitionIncorrect, InvalidCRC,
                                  InvalidResponse)
from powermon.ports import PortType
from powermon.protocols.abstractprotocol import AbstractProtocol

log = logging.getLogger("daly")

soc_construct = cs.Struct(
    "start_flag" / cs.Const(b"\xa5"),
    "module_address" / cs.Bytes(1),
    "command_id" / cs.Const(b"\x90"),
    "data_length" / cs.Byte,
    "battery_voltage" / cs.Int16ub,
    "acquistion_voltage" / cs.Int16ub,
    "current" / cs.Int16ub,
    "soc" / cs.Int16ub,
    "checksum" / cs.Bytes(1)
)

cvr_construct = cs.Struct(
    "start_flag" / cs.Const(b"\xa5"),
    "module_address" / cs.Bytes(1),
    "command_id" / cs.Const(b"\x91"),
    "data_length" / cs.Byte,
    "highest_voltage" / cs.Int16ub,
    "highest_cell" / cs.Byte,
    "lowest_voltage" / cs.Int16ub,
    "lowest_cell" / cs.Byte,
    "rest" / cs.Bytes(2),
    "checksum" / cs.Bytes(1)
)

temps_construct = cs.Struct(
    "start_flag" / cs.Const(b"\xa5"),
    "module_address" / cs.Bytes(1),
    "command_id" / cs.Const(b"\x92"),
    "data_length" / cs.Byte,
    "highest_temperature" / cs.Byte,
    "highest_sensor" / cs.Byte,
    "lowest_temperature" / cs.Byte,
    "lowest_sensor" / cs.Byte,
    "rest" / cs.Bytes(4),
    "checksum" / cs.Bytes(1)
)

mos_construct = cs.Struct(
    "start_flag" / cs.Const(b"\xa5"),
    "module_address" / cs.Bytes(1),
    "command_id" / cs.Const(b"\x93"),
    "data_length" / cs.Byte,
    "mode" / cs.Enum(cs.Int8sb, stationary=0, charging=1, discharging=2),
    "charging_mosfet" / cs.Byte,
    "discharging_mosfet" / cs.Byte,
    "bms_cycles" / cs.Int8ub,
    "capacity_ah" / cs.Int32ub,
    "checksum" / cs.Bytes(1)
)

status_construct = cs.Struct(
    "start_flag" / cs.Const(b"\xa5"),
    "module_address" / cs.Bytes(1),
    "command_id" / cs.Const(b"\x94"),
    "data_length" / cs.Byte,
    "number_of_cells" / cs.Int8sb,
    "number_of_temperature_sensors" / cs.Int8sb,
    "charger_running" / cs.Byte,
    "load_running" / cs.Byte,
    "states" / cs.BitStruct(
        "DO4" / cs.Flag,
        "DO3" / cs.Flag,
        "DO2" / cs.Flag,
        "DO1" / cs.Flag,
        "DI4" / cs.Flag,
        "DI3" / cs.Flag,
        "DI2" / cs.Flag,
        "DI1" / cs.Flag,
        ),
    "cycles" / cs.Int16ub,
    "rest" / cs.Bytes(1),
    "checksum" / cs.Bytes(1)
)


COMMANDS = {
    "SOC": {
        "name": "SOC",
        "aliases": ["soc", "state of charge", "default"],
        "description": "get the battery state of charge",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": "90",
        "result_type": ResultType.CONSTRUCT,
        "construct": soc_construct,
        "construct_min_response": 13,
        "reading_definitions": [
            {"index": "battery_voltage", "description": "Battery Bank Voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10"},
            # {"index": "acquistion_voltage", "description": "acquistion", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10"},
            {"index": "current", "description": "Current", "reading_type": ReadingType.CURRENT, "response_type": ResponseType.TEMPLATE_INT, "format_template": "(r-30000)/10"},
            {"index": "soc", "description": "SOC", "reading_type": ReadingType.PERCENTAGE, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10"},
        ],
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
        "aliases": ["cvr", "CVR"],
        "description": "get the highest and lowest cell voltage data",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": "91",
        "result_type": ResultType.CONSTRUCT,
        "construct": cvr_construct,
        "construct_min_response": 13,
        "reading_definitions": [
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
        "description": "get the highest and lowest temperature sensor data",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": "92",
        "result_type": ResultType.CONSTRUCT,
        "construct": temps_construct,
        "construct_min_response": 13,
        "reading_definitions": [
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
        "description": "get the bms mosfet states, bms cycles and battery capacity data",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": "93",
        "result_type": ResultType.CONSTRUCT,
        "construct": mos_construct,
        "construct_min_response": 13,
        # "result_type": ResultType.SINGLE,
        # "reading_definitions": [{"reading_type": ReadingType.MESSAGE, "description": "General Model Number", "response_type": ResponseType.BYTES}],
        "reading_definitions": [
            {"index": "mode", "description": "mode", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "charging_mosfet", "description": "charging_mosfet", "reading_type": ReadingType.ENABLED, "response_type": ResponseType.BOOL},
            {"index": "discharging_mosfet", "description": "discharging_mosfet", "reading_type": ReadingType.ENABLED, "response_type": ResponseType.BOOL},
            {"index": "bms_cycles", "description": "bms_cycles", "reading_type": ReadingType.NUMBER},
            {"index": "capacity_ah", "description": "capacity_ah", "reading_type": ReadingType.ENERGY, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
        ],
        "test_responses": [
            b'\xa5\x01\x93\x08\x02\x01\x01\x97\x00\x04-\xfa\x07',
        ],
    },
    "status": {
        "name": "status",
        "description": "get the number of cells, number of temperature sensors, charge and load states and bms cycle data",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": "94",
        "result_type": ResultType.CONSTRUCT,
        "construct": status_construct,
        "construct_min_response": 13,
        # "result_type": ResultType.SINGLE,
        # "reading_definitions": [{"reading_type": ReadingType.MESSAGE, "description": "General Model Number", "response_type": ResponseType.BYTES}],
        "reading_definitions": [
            {"index": "number_of_cells", "description": "number_of_cells", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "number_of_temperature_sensors", "description": "number_of_temperature_sensors", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "charger_running", "description": "charger_running", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.BOOL},
            {"index": "load_running", "description": "load_running", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.BOOL},
            #{"index": "DI2", "description": "states", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "cycles", "description": "cycles", "reading_type": ReadingType.NUMBER},
        ],
        "test_responses": [
            b'\xa5\x01\x94\x08\x10\x01\x00\x00\x02\x00\x1d\x88\xfa',
        ],
    },
    "cell_voltages": {
        "name": "cell_voltages",
        "description": "get the voltage of each battery cell",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": "95",
        "result_type": ResultType.BYTEARRAY,
        "construct_min_response": 13,
        "reading_definitions": [
            {"index": "cell_01_voltage", "description": "cell_01_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_02_voltage", "description": "cell_02_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_03_voltage", "description": "cell_03_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_04_voltage", "description": "cell_04_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_05_voltage", "description": "cell_05_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_06_voltage", "description": "cell_06_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_07_voltage", "description": "cell_07_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_08_voltage", "description": "cell_08_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_09_voltage", "description": "cell_09_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_10_voltage", "description": "cell_10_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_11_voltage", "description": "cell_11_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_12_voltage", "description": "cell_12_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_13_voltage", "description": "cell_13_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_14_voltage", "description": "cell_14_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_15_voltage", "description": "cell_15_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_16_voltage", "description": "cell_16_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_17_voltage", "description": "cell_17_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_18_voltage", "description": "cell_18_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_19_voltage", "description": "cell_19_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_20_voltage", "description": "cell_20_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_21_voltage", "description": "cell_21_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_22_voltage", "description": "cell_22_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_23_voltage", "description": "cell_23_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_24_voltage", "description": "cell_24_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_25_voltage", "description": "cell_25_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_26_voltage", "description": "cell_26_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_27_voltage", "description": "cell_27_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_28_voltage", "description": "cell_28_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_29_voltage", "description": "cell_29_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "cell_30_voltage", "description": "cell_30_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
        ],
        "test_responses": [
            b"\xa5\x01\x95\x08\x01\x0c\xfc\r\x10\r\x0f\x89\x0e\xa5\x01\x95\x08\x02\r3\x0c\xb7\r8\x89\x16\xa5\x01\x95\x08\x03\r\x10\r\x0f\r\x0e\x89#\xa5\x01\x95\x08\x04\r\x10\r\x10\r\x10\x89\'\xa5\x01\x95\x08\x05\r\x10\r\x0f\r\x10\x89\'\xa5\x01\x95\x08\x06\r\x0c\x00\x00\x00\x00\x89\xeb\xa5\x01\x95\x08\x07\x00\x00\x00\x00\x00\x00\x89\xd3\xa5\x01\x95\x08\x08\x00\x00\x00\x00\x00\x00\x89\xd4\xa5\x01\x95\x08\t\x00\x00\x00\x00\x00\x00\x89\xd5\xa5\x01\x95\x08\n\x00\x00\x00\x00\x00\x00\x89\xd6\xa5\x01\x95\x08\x0b\x00\x00\x00\x00\x00\x00\x89\xd7\xa5\xa8\x00@\x00\x00 @\x00\r0\x00\x00\x00 @\x00\x87K\x00\x00m2\x00\x00\x00 @\x00S1\x00\x00\x00\x00\x00\x00\xa8\x00\xa5\x01\x95\x08\x0f\x00\x00\x00\x00\x00\x00\x89\xdb\xa5\x01\x95\x08\x10\x00\x00\x00\x00\x00\x00\x89\xdc",
            b'\xa5\x01\x95\x08\x01\rU\rD\rN\x89\xdb\xa5\x01\x95\x08\x02\ra\r\\\rL\x89\xfe\xa5\x01\x95\x08\x03\rJ\rV\rT\x89\xea\xa5\x01\x95\x08\x04\rY\r^\rb\x89\x10\xa5\x01\x95\x08\x05\rR\r^\rX\x89\x00\xa5\x01\x95\x08\x06\rK\x00\x00\x00\x00\x89*\xa5\x01\x95\x08\x07\x00\x00\x00\x00\x00\x00\x89\xd3\xa5\x01\x95\x08\x08\x00\x00\x00\x00\x00\xa5\x01\x95\x08\t\x00\x00\x00\x00\x00\x00\x89\xd5\xa5\x01\x95\x08\n\x00\x00\x00\x00\x00\x00\x89\xd6\xa5\x01\x95\x08\x0b\x00\x00\x00\x00\x00\x00\x89\xd7\xa5\x01\x95\x08\xa8\x00@\x00\x00 @\x00\r0\x00\x00\x00 @\x00\xf3Z\x00\x00m2\x00\x00\x00 @\x00S1\x00\x00\x00\x00\x00\xa5\x01\x95\x08\x0f\x00\x00\x00\x00\x00\x00\x89\xdb\xa5\x01\x95\x08\x10\x00\x00\x00\x00\x00\x00\x89\xdc',
            b'\xd4\x0c\xd3\x0c\xd4\x82g\xa5\x01\x95\x08\x04\x0c\xd3\x0c\xd4\x0c\xd3\x82g\xa5\x01\x95\x08\x05\x0c\xd4\x0c\xd3\x0c\xd4\x82i\xa5\x01\x95\x08\x06\x0c\xd2\x0c\xd3\x0c\xd4\x82h\xa5\x01\x95\x08\x01\x0c\xd5\x0c\xd4\x0c\xd3\x82f\xa5\x01\x95\x08\x02\x0c\xd4\x0c\xd3\x0c\xd4\x82f\xa5\x01\x95\x08\x03\x0c\xd3\x0c\xd4\x0c\xd3\x82f\xa5\x01\x95\x08\x04\x0c\xd4\x0c\xd3\x0c\xd4\x82h\xa5\x01\x95\x08\x05\x0c\xd3\x0c\xd4\x0c\xd3\x82h\xa5\x01\x95\x08\x06\x0c\xd2\x0c\xd4\x0c\xd3\x82h\xa5\x01\x93\x08\x02\x01\x01\x1f\x00\x01\xa60;\xa5\x01\x96\x08\x017\x00\x00\x00\x00\x000\xac\xa5\x01\x94\x08\x10\x01\x00\x00\x00\x00\x0fT\xb6',
            b'{\xa5\x01\x95\x08\x06\x0c\xce\x0c\xd0\x0c\xd0\xa0{\xa5\x01\x95\x08\x01\x0c\xd1\x0c\xd0\x0c\xce\xa0w\xa5\x01\x95\x08\x02\x0c\xd0\x0c\xcf\x0c\xd0\xa0x\xa5\x01\x95\x08\x03\x0c\xcf\x0c\xd0\x0c\xcf\xa0x\xa5\x01\x95\x08\x04\x0c\xd0\x0c\xcf\x0c\xd0\xa0z\xa5\x01\x95\x08\x05\x0c\xcf\x0c\xd0\x0c\xcf\xa0z\xa5\x01\x95\x08\x06\x0c\xcf\x0c\xd0\x0c\xcf\xa0{',
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
        if response.count(b'\xa5') > 1:
            # multiframe response - length calc incorrect
            return True
        if response[0] != 0xa5:
            raise InvalidResponse("Response has incorrect start byte")
        if int(response[3]) != len(response[4:-1]):
            raise InvalidResponse("Response length does not match expected")
        return True

    def check_crc(self, response: str, command_definition: CommandDefinition = None) -> bool:
        """ crc check """
        log.debug("checking crc for %s", response)
        if response.count(b'\xa5') > 1:
            # multiframe response - crc calc incorrect
            return True
        calc_crc = sum(response[:-1]) & 0xFF
        response_crc = response[-1]

        if response_crc != calc_crc:
            raise InvalidCRC(f"response has invalid CRC - got '\\x{response_crc:02x}', calculated '\\x{calc_crc:02x}")
        # log.debug("Checksum matches in response '%s' response_crc:'%s'", response, calc_crc)
        return True

    def trim_response(self, response: str, command_definition: CommandDefinition = None) -> str:
        """ Remove extra characters from response """
        log.debug("response: %s", response)
        # remove any extra bytes at start - only for cell_voltages
        if command_definition.code == 'cell_voltages' and response[0] != 0xa5:
            response = response[response.find(0xa5):]
        return response

    def split_response(self, response: str, command_definition: CommandDefinition = None) -> list:
        """ split response into individual items, return as ordered list or list of tuples """
        result_type = getattr(command_definition, "result_type", None)
        log.debug("daly splitting %s, result_type %s", response, result_type)
        # build a list of (index, value) tuples, after parsing with a construct
        responses = []

        # parse response
        if command_definition.code == 'cell_voltages':
            # cell voltages have multiple frames - but sometimes not all of them
            # multiframe 'cell_voltages' struct to decode
            log.debug('daly multiframe decode')
            chunks = response.split(b'\xa5\x01')
            # remove the blank 'first result'
            chunks.pop(0)

            for chunk in chunks:
                # re-add inital bytes
                chunk = b'\xa5\x01' + chunk
                calc_crc = sum(chunk[:-1]) & 0xFF
                # ignore chunks with incorrect crc
                if calc_crc != chunk[-1]:
                    log.debug("chuck has incorrect crc: %s", chunk)
                    continue
                # ignore chunks with incorrect command code
                if chunk[2] != 0x95:
                    log.debug("chuck has incorrect command code: %s", chunk)
                    continue
                frame_number = chunk[4]
                if frame_number > 14:
                    log.debug("chuck frame number exceeds 14: %s", chunk)
                    continue
                cell_voltages = cs.Int16ub.parse(chunk[5:7]), cs.Int16ub.parse(chunk[7:9]), cs.Int16ub.parse(chunk[9:11])
                cell_number_offset = (frame_number - 1) * 3
                for i, cell_voltage in enumerate(cell_voltages):
                    if cell_voltage <= 0:
                        continue
                    # print(f'cell: {cell_number_offset + i + 1}, voltage: {cell_voltage}')
                    responses.append((f"cell_{cell_number_offset + i + 1:02d}_voltage", cell_voltage))
        else:
            # check for construct
            if command_definition.construct is None:
                raise CommandDefinitionIncorrect("No construct found in command_definition")
            if not command_definition.construct_min_response:
                raise CommandDefinitionIncorrect("No construct_min_response found in command_definition")
            if len(response) < command_definition.construct_min_response:
                raise InvalidResponse(f"response:{response}, len:{len(response)} too short for parsing (expecting {command_definition.construct_min_response:})")
            # parse with construct
            result = command_definition.construct.parse(response)
            # print(result)
            if result is None:
                log.debug("construct parsing returned None")
                return responses
            for x in result:
                match type(result[x]):
                    # case cs.ListContainer:
                    #     print(f"{x}:listcontainer")
                    case cs.Container:
                        # print(f"{x}:")
                        for y in result[x]:
                            if y != "_io":
                                key = y
                                value = result[x][y]
                                responses.append((key, value))
                    case _:
                        if x != "_io":
                            key = x
                            value = result[x]
                            responses.append((key, value))
        log.debug("responses: '%s'", responses)
        return responses
