""" protocols / neey.py """
# decode info from https://github.com/syssi/esphome-jk-bms/pull/145/files#diff-55d16e1a76e279db4f13bdef5b408d3c66daa537d85f6ee34861206495be3f63
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

operation_status = cs.Enum(cs.Int8sb, wrong_cell_count=1,
                                    AcqLine_Res_test=2,
                                    AcqLine_Res_exceed=3,
                                    Systest_Completed=4,
                                    Balancing=5,
                                    Balancing_finished=6,
                                    Low_voltage=7,
                                    System_Overtemp=8,
                                    Host_fails=9,
                                    Low_battery_voltage_balancing_stopped=10,
                                    Temperature_too_high_balancing_stopped=11,
                                    Self_test_completed=12,
)

cell_info_construct = cs.Struct(
    "start_flag" / cs.Bytes(2),
    "module_address" / cs.Bytes(1),
    "function" / cs.Bytes(1),
    "command" / cs.Int16ul,
    "length" / cs.Int16ul,
    "frame_counter" / cs.Byte,
    "cell_voltage_array" / cs.Array(24, cs.Float32l),
    "cell_resistance_array" / cs.Array(24, cs.Float32l),
    "total_voltage" / cs.Float32l,
    "average_cell_voltage" / cs.Float32l,
    "delta_cell_voltage" / cs.Float32l,
    "max_voltage_cell" / cs.Byte,
    "min_voltage_cell" / cs.Byte,
    "unknown" / cs.Bytes(1),
    "operation_status" / operation_status,
    "balancing_current" / cs.Float32l,
    "temperature_1" / cs.Float32l,
    "temperature_2" / cs.Float32l,
    "cell_detection_failed" / cs.Bytes(3),      # bitmask
    "cell_overvoltage_failed" / cs.Bytes(3),    # bitmask
    "cell_undervoltage_failed" / cs.Bytes(3),   # bitmask
    "cell_polarity_error" / cs.Bytes(3),        # bitmask
    "excessive_line_resistance" / cs.Bytes(3),  # bitmask
    "overheating" / cs.Bytes(1),  # bit 0 - sensor 1 warning, bit 1 - sensor 2
    "charging_fault" / cs.Bytes(1),  # 00: off, 01:on
    "discharge_fault" / cs.Bytes(1),  # 00: off, 01:on
    "read_write_error" / cs.Bytes(1),  # bit 0: read failed, bit 1 write failedd
    "unused" / cs.Bytes(6),
    "uptime" / cs.Float32l,
    "unused" / cs.Bytes(40),
    "crc" / cs.Bytes(1),
    "end_flag" / cs.Bytes(1),
)

settings_construct = cs.Struct(
    "start_flag" / cs.Bytes(2),
    "module_address" / cs.Bytes(1),
    "function" / cs.Bytes(1),  # 01 read
    "command" / cs.Int16ul,
    "length" / cs.Int16ul,
    "cell_count" / cs.Bytes(1),
    "balance_trigger_voltage" / cs.Float32l,
    "max_balance_current" / cs.Float32l,
    "balance_stop_voltage" / cs.Float32l,
    "balancing_enabled" / cs.Bytes(1),
    "buzzer_mode" / cs.Enum(cs.Byte, off=1, beep_once=2, beep_regular=3),
    "battery_type" / cs.Enum(cs.Byte, NCM=1, LFP=2, LTO=3, PbAc=4),
    "nominal_battery_capacity" / cs.Int32ul,
    "balance_start_voltage" / cs.Float32l,
    "unused" / cs.Bytes(66),
    "crc" / cs.Bytes(1),
    "end_flag" / cs.Bytes(1),
)

ack_construct = cs.Struct(
    "start_flag" / cs.Const(b'U\xaa'),
    "module_address" / cs.Bytes(1),
    "function" / cs.Bytes(1),  # 01 read
    "command" / cs.Int16ul,
    "length" / cs.Int16ul,
    "crc" / cs.Bytes(1),
    "end_flag" / cs.Const(b'\xff'),
)

defaults_construct = cs.Struct(
    "start_flag" / cs.Bytes(2),
    "module_address" / cs.Bytes(1),
    "function" / cs.Bytes(1),  # 01 read
    "command" / cs.Int16ul,
    "length" / cs.Int16ul,
    "standard_voltage_1" / cs.Float32l,
    "standard_voltage_2" / cs.Float32l,
    "battery_voltage_1" / cs.Float32l,
    "battery_voltage_2" / cs.Float32l,
    "standard_current_1" / cs.Float32l,
    "standard_current_2" / cs.Float32l,
    "superbat_1" / cs.Float32l,
    "superbat_2" / cs.Float32l,
    "resistor_1" / cs.Float32l,
    "battery_status" / cs.Bytes(4),
    "max_voltage" / cs.Float32l,
    "min_voltage" / cs.Float32l,
    "max_temperature" / cs.Float32l,
    "min_temperature" / cs.Float32l,
    "power_on_counter" / cs.Int32ul,
    "total_runtime" / cs.Int32ul,
    "production_date" / cs.Bytes(8),
    "unused" / cs.Bytes(18),
    "crc" / cs.Bytes(1),
    "end_flag" / cs.Bytes(1),
)

COMMANDS = {
    "info": {
        "name": "info",
        "aliases": ["device_info", "default"],
        "description": "get the balancer information",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": "01",
        "result_type": ResultType.CONSTRUCT,
        "construct": device_info_construct,
        "construct_min_response": 100,
        "reading_definitions": [
            {"index": "start_flag", "description": "start flag", "reading_type": ReadingType.IGNORE, "response_type": ResponseType.HEX_CHARS},
            {"index": "module_address", "description": "module address", "reading_type": ReadingType.IGNORE, "response_type": ResponseType.HEX_CHAR},
            {"index": "function", "description": "function", "reading_type": ReadingType.IGNORE, "response_type": ResponseType.HEX_CHAR},
            {"index": "command", "description": "command", "reading_type": ReadingType.IGNORE},
            {"index": "length", "description": "length", "reading_type": ReadingType.IGNORE},
            {"index": "crc", "description": "crc", "reading_type": ReadingType.IGNORE, "response_type": ResponseType.HEX_CHAR},
            {"index": "end_flag", "description": "end flag", "reading_type": ReadingType.IGNORE, "response_type": ResponseType.HEX_CHAR},

            {"index": "model", "description": "model", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.BYTES_STRIP_NULLS},
            {"index": "hw_version", "description": "hw_version", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.BYTES_STRIP_NULLS},
            {"index": "sw_version", "description": "sw_version", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.BYTES_STRIP_NULLS},
            {"index": "protocol_version", "description": "protocol_version", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.BYTES_STRIP_NULLS},
            {"index": "production_date", "description": "production_date", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.BYTES_STRIP_NULLS},
            {"index": "power_on_count", "description": "power_on_count", "reading_type": ReadingType.MESSAGE},
            {"index": "total_runtime", "description": "total_runtime", "reading_type": ReadingType.TIME_SECONDS},

        ],
        "test_responses": [
            b'U\xaa\x11\x01\x01\x00d\x00GW-24S4EB\x00\x00\x00\x00\x00\x00\x00HW-2.8.0ZH-1.2.3V1.0.0\x00\x0020220916\x04\x00\x00\x00n\x85?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00G\xff'
        ],
    },
    "cell_info": {
        "name": "cell_info",
        "description": "get the cell voltage, resistance information as well as battery voltage and balancing current",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": "02",
        "result_type": ResultType.CONSTRUCT,
        "construct": cell_info_construct,
        "construct_min_response": 300,
        "reading_definitions": [
            {"index": "operation_status", "description": "operation_status", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "balancing_current", "description": "balancing_current", "reading_type": ReadingType.CURRENT, "response_type": ResponseType.FLOAT},
            {"index": "total_voltage", "description": "total_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "average_cell_voltage", "description": "average_cell_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "delta_cell_voltage", "description": "delta_cell_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "max_voltage_cell", "description": "max_voltage_cell", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r+1"},
            {"index": "min_voltage_cell", "description": "min_voltage_cell", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r+1"},
            {"index": "cell_01_voltage", "description": "cell_01_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_02_voltage", "description": "cell_02_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_03_voltage", "description": "cell_03_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_04_voltage", "description": "cell_04_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_05_voltage", "description": "cell_05_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_06_voltage", "description": "cell_06_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_07_voltage", "description": "cell_07_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_08_voltage", "description": "cell_08_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_09_voltage", "description": "cell_09_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_10_voltage", "description": "cell_10_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_11_voltage", "description": "cell_11_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_12_voltage", "description": "cell_12_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_13_voltage", "description": "cell_13_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_14_voltage", "description": "cell_14_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_15_voltage", "description": "cell_15_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_16_voltage", "description": "cell_16_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_17_voltage", "description": "cell_17_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_18_voltage", "description": "cell_18_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_19_voltage", "description": "cell_19_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_20_voltage", "description": "cell_20_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_21_voltage", "description": "cell_21_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_22_voltage", "description": "cell_22_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_23_voltage", "description": "cell_23_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_24_voltage", "description": "cell_24_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "cell_01_resistance", "description": "cell_01_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_02_resistance", "description": "cell_02_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_03_resistance", "description": "cell_03_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_04_resistance", "description": "cell_04_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_05_resistance", "description": "cell_05_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_06_resistance", "description": "cell_06_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_07_resistance", "description": "cell_07_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_08_resistance", "description": "cell_08_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_09_resistance", "description": "cell_09_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_10_resistance", "description": "cell_10_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_11_resistance", "description": "cell_11_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_12_resistance", "description": "cell_12_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_13_resistance", "description": "cell_13_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_14_resistance", "description": "cell_14_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_15_resistance", "description": "cell_15_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_16_resistance", "description": "cell_16_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_17_resistance", "description": "cell_17_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_18_resistance", "description": "cell_18_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_19_resistance", "description": "cell_19_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_20_resistance", "description": "cell_20_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_21_resistance", "description": "cell_21_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_22_resistance", "description": "cell_22_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_23_resistance", "description": "cell_23_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "cell_24_resistance", "description": "cell_24_resistance", "reading_type": ReadingType.RESISTANCE, "response_type": ResponseType.FLOAT},
            {"index": "temperature_1", "description": "temperature_1", "reading_type": ReadingType.TEMPERATURE, "response_type": ResponseType.FLOAT},
            {"index": "temperature_2", "description": "temperature_2", "reading_type": ReadingType.TEMPERATURE, "response_type": ResponseType.FLOAT},
            {"index": "cell_detection_failed", "description": "cell_detection_failed", "reading_type": ReadingType.HEX_STR, "response_type": ResponseType.HEX_CHARS},
            {"index": "cell_overvoltage_failed", "description": "cell_overvoltage_failed", "reading_type": ReadingType.HEX_STR, "response_type": ResponseType.HEX_CHARS},
            {"index": "cell_undervoltage_failed", "description": "cell_undervoltage_failed", "reading_type": ReadingType.HEX_STR, "response_type": ResponseType.HEX_CHARS},
            {"index": "cell_polarity_error", "description": "cell_polarity_error", "reading_type": ReadingType.HEX_STR, "response_type": ResponseType.HEX_CHARS},
            {"index": "excessive_line_resistance", "description": "excessive_line_resistance", "reading_type": ReadingType.HEX_STR, "response_type": ResponseType.HEX_CHARS},
            {"index": "overheating", "description": "overheating", "reading_type": ReadingType.HEX_STR, "response_type": ResponseType.HEX_CHAR},
            {"index": "charging_fault", "description": "charging_fault", "reading_type": ReadingType.HEX_STR, "response_type": ResponseType.HEX_CHAR},
            {"index": "discharge_fault", "description": "discharge_fault", "reading_type": ReadingType.HEX_STR, "response_type": ResponseType.HEX_CHAR},
            {"index": "read_write_error", "description": "read_write_error", "reading_type": ReadingType.HEX_STR, "response_type": ResponseType.HEX_CHAR},
        ],
        "test_responses": [
            b'U\xaa\x11\x01\x02\x00,\x01\xed\xb2\x15S@4zT@\xe5}T@JuT@o{T@\xd0\x82T@ \x7fT@o{T@\xaflT@\x9aqT@\xf9xT@4zT@ \x7fT@_pT@[\x80T@\xb3\\T@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xee\x971>b9;>m\x852>\xb5\xf00>\x14R0>\xd1s3>\x86d5>\xdb\xaf7>f\xf7:>,\xa8@>\xb3)@>\x86\xcd=>\xf2W8>\xd3~3>\x19c1>^\xfe.>\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x9faTB\x9faT@\x00\x8f\xb6<\x05\x00\x0f\x05\xc4?\x81\xc0\xaeG\xf5A\xaeG\xf5A\x00\x00\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x8a\x8a\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xbe\xff'
        ],
    },
    "defaults": {
        "name": "defaults",
        "aliases": ["factory_defaults"],
        "description": "get the factory default settings",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": "03",
        "result_type": ResultType.CONSTRUCT,
        "construct": defaults_construct,
        "construct_min_response": 100,
        "reading_definitions": [
            {"index": "standard_voltage_1", "description": "standard_voltage_1", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "standard_voltage_2", "description": "standard_voltage_2", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "battery_voltage_1", "description": "battery_voltage_1", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "battery_voltage_2", "description": "battery_voltage_2", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "standard_current_1", "description": "standard_current_1", "reading_type": ReadingType.CURRENT, "response_type": ResponseType.FLOAT},
            {"index": "standard_current_2", "description": "standard_current_2", "reading_type": ReadingType.CURRENT, "response_type": ResponseType.FLOAT},
            {"index": "production_date", "description": "production_date", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "max_voltage", "description": "max_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "min_voltage", "description": "min_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "max_temperature", "description": "max_temperature", "reading_type": ReadingType.TEMPERATURE, "response_type": ResponseType.FLOAT},  # F?
            {"index": "min_temperature", "description": "min_temperature", "reading_type": ReadingType.TEMPERATURE, "response_type": ResponseType.FLOAT},  # F?
            {"index": "total_runtime", "description": "total_runtime", "reading_type": ReadingType.TIME_SECONDS},
            {"index": "power_on_counter", "description": "power_on_counter", "reading_type": ReadingType.NUMBER},
            {"index": "superbat_1", "description": "superbat_1", "reading_type": ReadingType.NUMBER, "response_type": ResponseType.FLOAT},
            {"index": "superbat_2", "description": "superbat_2", "reading_type": ReadingType.NUMBER, "response_type": ResponseType.FLOAT},
            {"index": "resistor_1", "description": "resistor_1", "reading_type": ReadingType.NUMBER, "response_type": ResponseType.FLOAT},
            {"index": "battery_status", "description": "battery_status", "reading_type": ReadingType.HEX_STR, "response_type": ResponseType.HEX_CHAR},
        ],
        "test_responses": [
            b'U\xaa\x11\x01\x03\x00\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00(\xffU\xaa\x11\x01\x03\x00d\x00`\x1b\xbf?@(\xbf?\n\x9eK@33s@"p\xd5?0\xe7\xd4?\x7f\xf2\x00@\x00\x00\x00\x00\x00\x00\x80?33\xd3?\\\x8f\xd2?H\xe1\xba?\x00\x00\xaaB\x00\x00\x82B\x04\x00\x00\x00~\x11E\x0020220916\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x97\xff'
        ],
    },
    "settings": {
        "name": "settings",
        "aliases": ["get_settings"],
        "description": "get the bms settings",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": "04",
        "result_type": ResultType.CONSTRUCT,
        "construct": settings_construct,
        "construct_min_response": 100,
        "reading_definitions": [
            {"index": "cell_count", "description": "cell_count", "reading_type": ReadingType.NUMBER, "response_type": ResponseType.HEX_CHAR},
            {"index": "balance_trigger_voltage", "description": "balance_trigger_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "balance_stop_voltage", "description": "balance_stop_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "balance_start_voltage", "description": "balance_start_voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
            {"index": "max_balance_current", "description": "max_balance_current", "reading_type": ReadingType.CURRENT, "response_type": ResponseType.FLOAT},
            {"index": "nominal_battery_capacity", "description": "nominal_battery_capacity", "reading_type": ReadingType.ENERGY},
            {"index": "balancing", "description": "balancing_enabled", "reading_type": ReadingType.ENABLED},
            {"index": "buzzer_mode", "description": "buzzer_mode", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "battery_type", "description": "battery_type", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
        ],
        "test_responses": [
            b'U\xaa\x11\x01\x04\x00d\x00\x10\n\xd7\xa3;\x00\x00\x80@\x00\x00 @\x01\x01\x02\x18\x01\x00\x00ff&@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xb7\xff'
        ],
    },
}

SETTER_COMMANDS = {
    "on": {
        "name": "on",
        "aliases": ["balancer_on"],
        "description": "turn balancer on",
        "result_type": ResultType.SINGLE,
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": 0x0d05,
        "command_data": 0x01,
        "reading_definitions": [
            {"description": "result", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.HEX_CHAR},
        ],
        "test_responses": [ 
            b'U\xaa\x11\x00\x05\r\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006\xff',
        ],
    },
    "off": {
        "name": "off",
        "aliases": ["balancer_off"],
        "description": "turn balancer off",
        "result_type": ResultType.SINGLE,
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": 0x0d05,
        "reading_definitions": [
            {"description": "result", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.HEX_CHAR},
        ],
        "test_responses": [
            b'U\xaa\x11\x00\x05\r\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006\xff',
        ],
    },
    "buzzer_mode": {
        "name": "buzzer_mode",
        "description": "set the buzzer mode",
        "help": "  -- eg buzzer_mode=1 (set buzzer off) off=1, beep_once=2, beep_regular=3",
        "result_type": ResultType.SINGLE,
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": 0x1405,
        "reading_definitions": [
            {"description": "result", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.HEX_CHAR},
        ],
        "test_responses": [
            b'U\xaa\x11\x00\x05\r\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006\xff',
        ],
        "regex": "buzzer_mode=([123])$",
    },
    "battery_type": {
        "name": "battery_type",
        "description": "set the battery type",
        "help": "  -- eg battery_type=2 (set battery type to LFP) NCM=1, LFP=2, LTO=3, PbAc=4",
        "result_type": ResultType.SINGLE,
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": 0x1505,
        "reading_definitions": [
            {"description": "result", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.HEX_CHAR},
        ],
        "test_responses": [
            b'U\xaa\x11\x00\x05\r\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006\xff',
        ],
        "regex": "battery_type=([1234])$",
    },
    "cell_count": {
        "name": "cell_count",
        "description": "set the number of cells in the battery",
        "result_type": ResultType.SINGLE,
        "help": "  -- eg cell_count=4 (set cell count to 4)",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": 0x0105,
        "reading_definitions": [
            {"description": "result", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.HEX_CHAR},
        ],
        "test_responses": [
            b'U\xaa\x11\x01\x04\x00d\x00\x10\n\xd7\xa3;\x00\x00\x80@\x00\x00 @\x00\x01\x02,\x01\x00\x00ff&@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xca\xff',
        ],
        "regex": r"cell_count=(\d+)$",
    },
    "max_balance_current": {
        "name": "max_balance_current",
        "aliases": ["mbc", "balance_current"],
        "description": "set the maximum balance current",
        "result_type": ResultType.SINGLE,
        "help": "  -- eg max_balance_current=4.0 (set max balance current to 4.0A)",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": 0x0305,
        "reading_definitions": [
            {"description": "result", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.HEX_CHAR},
        ],
        "test_responses": [
            b'U\xaa\x11\x00\x05\x03\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00,\xff',
            b'U\xaa\x11\x00\x05\x03\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00,\xff',
        ],
        "regex": r"(?:balance_current|mbc|max_balance_current)=(\d+(?:\.\d+)?)",
    },
    "device_name": {
        "name": "device_name",
        "description": "set the BLE device name",
        "result_type": ResultType.SINGLE,
        "help": "  -- eg device_name=test",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": 0x1305,
        "reading_definitions": [
            {"description": "result", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.HEX_CHAR},
        ],
        "test_responses": [
            b'U\xaa\x11\x00\x05\x13\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00<\xff',
        ],
        "regex": r"device_name=(.+)$",
    },
    "nominal_battery_capacity": {
        "name": "nominal_battery_capacity",
        "aliases": ["battery_capacity", "capacity"],
        "description": "set the nominal battery capacity",
        "result_type": ResultType.SINGLE,
        "help": "  -- eg nominal_battery_capacity=300 (set capacity to 300Ah)",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": 0x1605,
        "reading_definitions": [
            {"description": "result", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.HEX_CHAR},
        ],
        "test_responses": [
            b'U\xaa\x11\x00\x05\x03\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00,\xff',
        ],
        "regex": r"(?:nominal_battery_capacity|battery_capacity|capacity)=(\d+)$",
    },
    "balance_trigger_voltage": {
        "name": "balance_trigger_voltage",
        "aliases": ["trigger_voltage", ],
        "description": "set the voltage difference above which balancing will start",
        "result_type": ResultType.SINGLE,
        "help": "  -- eg balance_trigger_voltage=0.4 (start balancing when cell voltage difference is greater than 0.4V)",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": 0x0205,
        "reading_definitions": [
            {"description": "result", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.HEX_CHAR},
        ],
        "test_responses": [
            b'U\xaa\x11\x00\x05\x03\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00,\xff',
        ],
        "regex": r"(?:balance_trigger_voltage|trigger_voltage)=(\d+(?:\.\d+)?)",
    },
    "balance_stop_voltage": {
        "name": "balance_stop_voltage",
        "aliases": ["stop_voltage", ],
        "description": "set the voltage below which balancing will stop",
        "result_type": ResultType.SINGLE,
        "help": "  -- eg balance_stop_voltage=2.5 (stop balancing when voltage drops below 2.5V)",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": 0x0405,
        "reading_definitions": [
            {"description": "result", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.HEX_CHAR},
        ],
        "test_responses": [
            b'U\xaa\x11\x00\x05\x03\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00,\xff',
        ],
        "regex": r"(?:balance_stop_voltage|stop_voltage)=(\d+(?:\.\d+)?)",
    },
    "balance_start_voltage": {
        "name": "balance_start_voltage",
        "aliases": ["start_voltage", ],
        "description": "set the voltage above which balancing will start",
        "result_type": ResultType.SINGLE,
        "help": "  -- eg balance_start_voltage=2.2 (start balancing when voltage rises above 2.2V)",
        "command_type": CommandType.SERIAL_READ_UNTIL_DONE,
        "command_code": 0x1705,
        "reading_definitions": [
            {"description": "result", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.HEX_CHAR},
        ],
        "test_responses": [
            b'U\xaa\x11\x00\x05\x03\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00,\xff',
        ],
        "regex": r"(?:balance_start_voltage|start_voltage)=(\d+(?:\.\d+)?)",
    },
}

# TODO: test on / off commands
# TODO: implement other setter commands

# Factory defaults
#
# standardVol2   ReferenceVoltage [0.001f, 5.0f]: Set 1.0f             aa551100 0505 1400 0000803f000000000000 45ff
# battery_vol    BatteryVoltage [0.001f, 5.0f]: Set 1.0f               aa551100 0506 1400 0000803f000000000000 46ff
# standardCur2   Balancing Current Default? [0.001f, 5.0f]: Set 1.0f   aa551100 0507 1400 0000803f000000000000 47ff
# superBat2      Mean SuperCap Voltage [0.001f, 5.0f]: Set 1.0f        aa551100 050e 1400 0000803f000000000000 4eff
# triger_mpa     StartVol(V) [0.001f, 5.0f]: Set 1.0f                  aa551100 0508 1400 0000803f000000000000 48ff
# open_num       Boot count []: Set 1.0f                               aa551100 0509 1400 0000803f000000000000 49ff
# batStatu       RefBat Vol [0.001f, 5.0f]: Set 1.0f                   aa551100 050f 1400 0000803f000000000000 4fff
# battery_max    BatMax [0.001f, 5.0f]: Set 1.0f                       aa551100 050b 1400 0000803f000000000000 4bff
# battery_min    BatMin [0.001f, 5.0f]: Set 1.0f                       aa551100 050c 1400 0000803f000000000000 4cff
# ntc_max        NtcMax [-19.9f, 120.0f]: Set 1.0f                     aa551100 0511 1400 0000803f000000000000 51ff
# ntc_min        NtcMin [-19.9f, 120.0f]: Set 1.0f                     aa551100 0512 1400 0000803f000000000000 52ff
# total_time     Working time []: Set 1                                aa551100 050a 1400 01000000000000000000 f4ff
# cycle          Production date: Set 20220802                         aa551100 0510 1400 32303232303830320000 e7ff


class Neey(AbstractProtocol):
    """
    Neey Active Balancer protocol handler
    """

    def __str__(self):
        return "NEEY Active Balancer protocol handler"

    def __init__(self) -> None:
        super().__init__()
        self.protocol_id = b"NEEY"
        self.add_command_definitions(COMMANDS)
        # self.add_command_definitions(SETTER_COMMANDS, result_type=ResultType.ACK)
        self.add_command_definitions(SETTER_COMMANDS)
        self.add_supported_ports([PortType.BLE])
        self.notifier_handle = 9
        self.intializing_handle = 0
        self.command_handle = 15
        self.check_definitions_count(expected=None)

    def get_full_command(self, command: bytes|str) -> bytes:
        log.info("Using protocol %s with %i commands", self.protocol_id, len(self.command_definitions))

        command_definition : CommandDefinition = self.get_command_definition(command)
        if command_definition is None:
            return None

        data_length = cs.Int16ul.build(20)

        # fix a 'bug' that seems to be implemented on the device?
        if command_definition.code == "cell_info":
            data_length = cs.Int16ub.build(20)

        command_bytes = cs.Int16ul.build(int(command_definition.command_code))
        function = 0x01
        if command_definition.result_type == ResultType.SINGLE:
            function = 0x00
        # _data = bytearray()
        command_data = bytearray(10)
        if command_definition.command_data is not None:
            command_data = cs.Int16ul.build(int(command_definition.command_data))
        if command_definition.match is not None:
            # got a regex matched command
            # group 1 is 'data'
            # TODO: fix this - maybe a SETTER type and checking etc?
            # Some commands have FLOAT encoding (ie 1.0 -> 0000803f)
            if command_definition.command_code in [0x1705, 0x0405, 0x0305, 0x0205]:
                command_data = cs.Float32l.build(float(command_definition.match.group(1)))
            # Other have TEXT encoded
            elif command_definition.command_code in [0x1305,]:
                for i, _chr in enumerate(command_definition.match.group(1)):
                    command_data[i] = ord(_chr)
            # Otherwise default to INT/Int16ul encoding (ie int 4 -> 04)
            else:
                command_data = cs.Int64ul.build(int(command_definition.match.group(1)))


        # print(command_definition)

        full_command = bytearray(20)
        full_command[0] = 0xaa  # start flag
        full_command[1] = 0x55  # start flag
        full_command[2] = 0x11  # module address
        full_command[3] = function  # function
        full_command[4] = command_bytes[0]  # command code
        full_command[5] = command_bytes[1]  # command code
        full_command[6] = data_length[0]  # length
        full_command[7] = data_length[1]  # length
        for i, x in enumerate(command_data):
            full_command[8+i] = x
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

    def checksum(self, response: bytes) -> int:
        """Calculate neey checksum of supplied bytes (OR of each byte)

        Args:
            response (_type_): bytes to calculate checksum of

        Returns:
            int: calculated checksum
        """
        calc_crc = 0
        for i in response:
            calc_crc = calc_crc ^ i
        return calc_crc

    def crc(self, response: bytes) -> int:
        """Calculate neey crc of supplied bytes (sum bytes & 0xFF)

        Args:
            response (bytes): bytes to calculate crc of

        Returns:
            int: calculated crc
        """
        return sum(response) & 0xFF

    def check_crc(self, response: str, command_definition: CommandDefinition = None) -> bool:
        """ crc check, needs override in protocol """
        log.debug("checking crc for %s", response)
        if response.count(b'U\xaa') > 1:
            # multiframe response
            # check last frame...
            last_frame = response.rfind(b'U\xaa')
            response = response[last_frame:]
        calc_crc = self.crc(response[:-2])
        response_crc = response[-2]

        if response_crc != calc_crc:
            raise InvalidCRC(f"response has invalid CRC - got '\\x{response_crc:02x}', calculated '\\x{calc_crc:02x}")
        # log.debug("Checksum matches in response '%s' response_crc:'%s'", response, calc_crc)
        return True

    def trim_response(self, response: str, command_definition: CommandDefinition = None) -> str:
        """ Remove extra characters from response """
        log.debug("response: %s", response)
        last_frame = response.rfind(b'U\xaa')
        return response[last_frame:]

    def split_response(self, response: str, command_definition: CommandDefinition = None) -> list:
        """ split response into individual items, return as ordered list or list of tuples """
        result_type = getattr(command_definition, "result_type", None)
        log.debug("daly splitting %s, result_type %s", response, result_type)
        # build a list of (index, value) tuples, after parsing with a construct
        responses = []
        if command_definition.result_type == ResultType.SINGLE:
            responses.append(("result", response))
            return responses
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
            # print(x)
            if x == "_io":
                continue
            elif x == 'cell_voltage_array':
                # print("cell_voltages")
                for i, value in enumerate(result[x]):
                    # print(i+1,cell)
                    if value:  # explicit exclusion of 0 value results
                        key = f"cell_{i+1:02d}_voltage"
                        responses.append((key,value))
            elif x == 'cell_resistance_array':
                for i, value in enumerate(result[x]):
                    # print(i+1,cell)
                    if value:  # explicit exclusion of 0 value results
                        key = f"cell_{i+1:02d}_resistance"
                        responses.append((key,value))
            else:
                key = x
                value = result[x]
                responses.append((key, value))
        log.debug("responses: '%s'", responses)
        return responses
