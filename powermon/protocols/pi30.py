""" pi30.py """
import logging

from powermon.commands.command_definition import CommandCategory, CommandDefinition
from powermon.commands.reading_definition import ReadingDefinition, ReadingType, ResponseType
from powermon.commands.result import ResultType
from powermon.libs.errors import InvalidCRC, InvalidResponse
from powermon.ports import PortType
from powermon.protocols.abstractprotocol import AbstractProtocol
from powermon.protocols.constants import (BATTERY_TYPES, CHARGER_SOURCE_PRIORITIES, FAULT_CODE_OPTIONS,
                                          FAULT_CODE_OPTIONS_PI30MAX, INVERTER_MODE_OPTIONS, OUTPUT_MODES,
                                          OUTPUT_SOURCE_PRIORITIES, PI30_OUTPUT_MODES)
from powermon.protocols.helpers import crc_pi30 as crc

log = logging.getLogger("pi30")

# PI30 QUERY COMMANDS
QPI = {
    "name": "QPI",
    "description": "Get the Inverter supported Protocol ID",
    "category": CommandCategory.INFO,
    "result_type": ResultType.SINGLE,
    "reading_definitions": [{"description": "Protocol Id", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.BYTES}],
    "test_responses": [b"(PI30\x9a\x0b\r"],
    }
QID = {
    "name": "QID",
    "aliases": ["get_id", "default"],
    "description": "Get the Serial Number of the Inverter",
    "category": CommandCategory.INFO,
    "result_type": ResultType.SINGLE,
    "reading_definitions": [{"description": "Serial Number", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING}],
    "test_responses": [b"(9293333010501\xbb\x07\r"],
    }
QVFW = {
    "name": "QVFW",
    "description": "Get the Main CPU firmware version",
    "category": CommandCategory.INFO,
    "result_type": ResultType.SINGLE,
    "reading_definitions": [{"reading_type": ReadingType.MESSAGE, "description": "Main CPU firmware version", "response_type": ResponseType.TEMPLATE_BYTES, "format_template" : "r.removeprefix('VERFW:')"}],
    "test_responses": [b"(VERFW:00072.70\x53\xA7\r"],
    }
QVFW2 = {
    "name": "QVFW2",
    "description": "Get the Secondary CPU firmware version",
    "category": CommandCategory.INFO,
    "result_type": ResultType.SINGLE,
    "reading_definitions": [{"reading_type": ReadingType.MESSAGE, "description": "Secondary CPU firmware version", "response_type": ResponseType.TEMPLATE_BYTES, "format_template" : "r.removeprefix('VERFW:')"}],
    "test_responses": [b"(VERFW:00072.70\x53\xA7\r"],
    }
QBOOT = {
    "name": "QBOOT",
    "description": "Get DSP Has Bootstrap",
    "category": CommandCategory.DATA,
    "result_type": ResultType.SINGLE,
    "reading_definitions": [{"description": "DSP Has Bootstrap", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.BOOL}],
    "test_responses": [b"(0\xb9\x1c\r"],
    }
QDI = {
    "name": "QDI",
    "description": "Get the Inverters Default Settings",
    "category": CommandCategory.DEFAULTS,
    "result_type": ResultType.ORDERED,
    "reading_definitions": [
        {"description": "AC Output Voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
        {"description": "AC Output Frequency", "reading_type": ReadingType.FREQUENCY, "response_type": ResponseType.FLOAT},
        {"description": "Max AC Charging Current", "reading_type": ReadingType.CURRENT, "response_type": ResponseType.INT},
        {"description": "Battery Under Voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
        {"description": "Battery Float Charge Voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
        {"description": "Battery Bulk Charge Voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
        {"description": "Battery Recharge Voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
        {"description": "Max Charging Current", "reading_type": ReadingType.CURRENT, "response_type": ResponseType.INT},
        {"description": "Input Voltage Range", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": ["Appliance", "UPS"]},
        {"description": "Output Source Priority", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority",
            "reading_type": ReadingType.MESSAGE,
            "response_type": ResponseType.LIST,
            "options": ["Utility first", "Solar first", "Solar + Utility", "Solar only"]},
        {"description": "Battery Type", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": BATTERY_TYPES},
        {"description": "Buzzer", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": ["enabled", "disabled"]},
        {"description": "Power saving", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": ["disabled", "enabled"]},
        {"description": "Overload restart", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": ["disabled", "enabled"]},
        {"description": "Over temperature restart", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": ["disabled", "enabled"]},
        {"description": "LCD Backlight", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": ["disabled", "enabled"]},
        {"description": "Primary source interrupt alarm", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": ["disabled", "enabled"]},
        {"description": "Record fault code", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": ["disabled", "enabled"]},
        {"description": "Overload bypass", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": ["disabled", "enabled"]},
        {"description": "LCD reset to default", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": ["disabled", "enabled"]},
        {"description": "Output mode", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_MODES},
        {"description": "Battery Redischarge Voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
        {"description": "PV OK condition",
            "reading_type": ReadingType.MESSAGE,
            "response_type": ResponseType.LIST,
            "options":
            ["As long as one unit of inverters has connect PV, parallel system will consider PV OK",
                "Only All of inverters have connect PV, parallel system will consider PV OK"]},
        {"description": "PV Power Balance",
            "reading_type": ReadingType.MESSAGE,
            "response_type": ResponseType.LIST,
            "options":
            ["PV input max current will be the max charged current",
                "PV input max power will be the sum of the max charged power and loads power"]},
        {"description": "Unknown Value", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.BYTES},
    ],
    "test_responses": [
        b"(230.0 50.0 0030 42.0 54.0 56.4 46.0 60 0 0 2 0 0 0 0 0 1 1 0 0 1 0 54.0 0 1 000\x9E\x60\r",
        b"(230.0 50.0 0030 44.0 54.0 56.4 46.0 60 0 0 2 0 0 0 0 0 1 1 1 0 1 0 54.0 0 1 224\xeb\xbc\r",
        b"(230.0 50.0 0030 44.0 54.0 56.4 46.0 60 0 0 2 0 0 0 0 0 1 1 1 0 1 7 54.0 0 1 224\x9b\xba\r",],
    }
QMN = {
    "name": "QMN",
    "description": "Get the Model Name",
    "category": CommandCategory.INFO,
    "result_type": ResultType.SINGLE,
    "reading_definitions": [{"reading_type": ReadingType.MESSAGE, "description": "Model Name", "response_type": ResponseType.BYTES}],
    "test_responses": [b"(MKS2-8000\xb2\x8d\r",],
    }
QGMN = {
    "name": "QGMN",
    "description": "Get the General Model Number",
    "category": CommandCategory.INFO,
    "result_type": ResultType.SINGLE,
    "reading_definitions": [{"reading_type": ReadingType.MESSAGE, "description": "General Model Number", "response_type": ResponseType.BYTES}],
    "test_responses": [b"(044\xc8\xae\r",],
    }
QMCHGCR = {
    "name": "QMCHGCR",
    "description": "Get the viable options for Max Charging Current",
    "category": CommandCategory.INFO,
    "result_type": ResultType.MULTIVALUED,
    "reading_definitions": [{"reading_type": ReadingType.MESSAGE_AMPS, "description": "Max Charging Current Options", "response_type": ResponseType.STRING}],
    "test_responses": [b"(010 020 030 040 050 060 070 080 090 100 110 120\x0c\xcb\r"], 
    }
QMUCHGCR = {
    "name": "QMUCHGCR",
    "description": "Get the viable options for Max Utility Charging Current",
    "category": CommandCategory.INFO,
    "result_type": ResultType.MULTIVALUED,
    "reading_definitions": [{"reading_type": ReadingType.MESSAGE_AMPS, "description": "Max Utility Charging Current", "response_type": ResponseType.STRING}],
    "test_responses": [b"(002 010 020 030 040 050 060 070 080 090 100 110 120\xca#\r"], 
    }
QOPM = {
    "name": "QOPM",
    "description": "Get the Inverter Output Mode",
    "category": CommandCategory.INFO,
    "result_type": ResultType.SINGLE,
    "reading_definitions": [{"description": "Output mode", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_MODES}],
    "test_responses": [b"(0\xb9\x1c\r", b"(7\xc9\xfb\r"], 
    }
QPIGS = {
    "name": "QPIGS",
    "description": "Get the current values of various General Status parameters",
    "category": CommandCategory.DATA,
    "result_type": ResultType.ORDERED,
    "reading_definitions": [
        {"description": "AC Input Voltage",
            "reading_type": ReadingType.VOLTS,
            "response_type": ResponseType.FLOAT,
            "icon": "mdi:transmission-tower-export",
            "device_class": "voltage"},
        {"description": "AC Input Frequency", "reading_type": ReadingType.FREQUENCY, "response_type": ResponseType.FLOAT, "icon": "mdi:current-ac", "device_class": "frequency"},
        {"description": "AC Output Voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT, "icon": "mdi:power-plug", "device_class": "voltage"},
        {"description": "AC Output Frequency", "reading_type": ReadingType.FREQUENCY, "response_type": ResponseType.FLOAT, "icon": "mdi:current-ac", "device_class": "frequency"},
        {"description": "AC Output Apparent Power", "reading_type": ReadingType.APPARENT_POWER, "response_type": ResponseType.INT, "icon": "mdi:power-plug", "device_class": "apparent_power"},
        {"description": "AC Output Active Power", "reading_type": ReadingType.WATTS, "response_type": ResponseType.INT, "icon": "mdi:power-plug", "device_class": "power", "state_class": "measurement"},
        {"description": "AC Output Load", "reading_type": ReadingType.PERCENTAGE, "response_type": ResponseType.INT, "icon": "mdi:brightness-percent"},
        {"description": "BUS Voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.INT, "icon": "mdi:details", "device_class": "voltage"},
        {"description": "Battery Voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT, "icon": "mdi:battery-outline", "device_class": "voltage"},
        {"description": "Battery Charging Current", "reading_type": ReadingType.CURRENT, "response_type": ResponseType.INT, "icon": "mdi:current-dc", "device_class": "current"},
        {"description": "Battery Capacity", "reading_type": ReadingType.PERCENTAGE, "response_type": ResponseType.INT, "device_class": "battery"},
        {"description": "Inverter Heat Sink Temperature", "reading_type": ReadingType.TEMPERATURE, "response_type": ResponseType.INT, "icon": "mdi:details", "device_class": "temperature"},
        {"description": "PV Input Current", "reading_type": ReadingType.CURRENT, "response_type": ResponseType.FLOAT, "icon": "mdi:solar-power", "device_class": "current"},
        {"description": "PV Input Voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT, "icon": "mdi:solar-power", "device_class": "voltage"},
        {"description": "Battery Voltage from SCC", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT, "icon": "mdi:battery-outline", "device_class": "voltage"},
        {"description": "Battery Discharge Current", "reading_type": ReadingType.CURRENT, "response_type": ResponseType.INT, "icon": "mdi:battery-negative", "device_class": "current"},
        {"description": "Device Status",
            "reading_type": ReadingType.FLAGS,
            "response_type": ResponseType.FLAGS,
            "flags": [
                "Is SBU Priority Version Added",
                "Is Configuration Changed",
                "Is SCC Firmware Updated",
                "Is Load On",
                "Is Battery Voltage to Steady While Charging",
                "Is Charging On",
                "Is SCC Charging On",
                "Is AC Charging On",
            ]},
        {"description": "RSV1", "reading_type": ReadingType.CURRENT, "response_type": ResponseType.INT},
        {"description": "RSV2", "reading_type": ReadingType.CURRENT, "response_type": ResponseType.INT},
        {"description": "PV Input Power", "reading_type": ReadingType.WATTS, "response_type": ResponseType.INT, "icon": "mdi:solar-power", "device_class": "power", "state_class": "measurement"},
        {"description": "Device Status2", "reading_type": ReadingType.FLAGS, "response_type": ResponseType.FLAGS, "flags": ["Is Charging to Float", "Is Switched On", "Is Dustproof Installed"]},
    ],
    "test_responses": [
        b"(000.0 00.0 230.0 49.9 0161 0119 003 460 57.50 012 100 0069 0014 103.8 57.45 00000 00110110 00 00 00856 010\x24\x8c\r",
        b"(227.2 50.0 230.3 50.0 0829 0751 010 447 54.50 020 083 0054 02.7 323.6 00.00 00000 00010110 00 00 00879 010\xf1\x8c\r",
        b"(227.2 50.0 230.3 50.0 0829 0751 010 447 54.50 020 083 0054 02.7 323.6 00.00 00000 00010110 00 00 00879 010 1 02 123\x1c\x84\r",
    ],
    }
QPIRI = {
    "name": "QPIRI",
    "description": "Get the current Settings of the Inverter",
    "category": CommandCategory.SETTINGS,
    "result_type": ResultType.ORDERED,
    "reading_definitions": [
        {"description": "AC Input Voltage", "reading_type": ReadingType.VOLTS, "icon": "mdi:transmission-tower-import", "device_class": "voltage", "response_type": ResponseType.FLOAT},
        {"description": "AC Input Current", "reading_type": ReadingType.CURRENT, "icon": "mdi:current-ac", "device_class": "current", "response_type": ResponseType.FLOAT},
        {"description": "AC Output Voltage", "reading_type": ReadingType.VOLTS,  "icon": "mdi:transmission-tower-export", "device_class": "voltage", "response_type": ResponseType.FLOAT},
        {"description": "AC Output Frequency", "reading_type": ReadingType.FREQUENCY, "icon": "mdi:current-ac", "device_class": "frequency", "response_type": ResponseType.FLOAT},
        {"description": "AC Output Current", "reading_type": ReadingType.CURRENT, "icon": "mdi:current-ac", "device_class": "current", "response_type": ResponseType.FLOAT},
        {"description": "AC Output Apparent Power", "reading_type": ReadingType.APPARENT_POWER, "icon": "mdi:power-plug", "device_class": "apparent_power"},
        {"description": "AC Output Active Power", "reading_type": ReadingType.WATTS, "icon": "mdi:power-plug", "device_class": "power", "state_class": "measurement"},
        {"description": "Battery Voltage", "reading_type": ReadingType.VOLTS, "icon": "mdi:battery-outline", "device_class": "voltage","response_type": ResponseType.FLOAT},
        {"description": "Battery Recharge Voltage", "reading_type": ReadingType.VOLTS, "icon": "mdi:battery-outline", "device_class": "voltage", "response_type": ResponseType.FLOAT},
        {"description": "Battery Under Voltage", "reading_type": ReadingType.VOLTS, "icon": "mdi:battery-outline", "device_class": "voltage", "response_type": ResponseType.FLOAT},
        {"description": "Battery Bulk Charge Voltage", "reading_type": ReadingType.VOLTS, "icon": "mdi:battery-outline", "device_class": "voltage", "response_type": ResponseType.FLOAT},
        {"description": "Battery Float Charge Voltage", "reading_type": ReadingType.VOLTS, "icon": "mdi:battery-outline", "device_class": "voltage", "response_type": ResponseType.FLOAT},
        {"description": "Battery Type", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": BATTERY_TYPES},
        {"description": "Max AC Charging Current", "reading_type": ReadingType.CURRENT, "icon": "mdi:current-ac", "device_class": "current"},
        {"description": "Max Charging Current", "reading_type": ReadingType.CURRENT, "icon": "mdi:current-ac", "device_class": "current"},
        {"description": "Input Voltage Range", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": ["Appliance", "UPS"]},
        {"description": "Output Source Priority", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": ["Utility first", "Solar first", "Solar + Utility", "Solar only"]},
        {"description": "Max Parallel Units", "reading_type": ReadingType.MESSAGE, "default": "not set"},
        {"description": "Machine Type", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.OPTION, "options": {"00": "Grid tie", "01": "Off Grid", "10": "Hybrid"}},
        {"description": "Topology", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": ["transformerless", "transformer"]},
        {"description": "Output Mode", "reading_type": ReadingType.MESSAGE, "device_class": "enum", "response_type": ResponseType.LIST, "options": OUTPUT_MODES},
        {"description": "Battery Redischarge Voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
        {"description": "PV OK Condition",
            "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST,
            "options": ["As long as one unit of inverters has connect PV, parallel system will consider PV OK",
                        "Only All of inverters have connect PV, parallel system will consider PV OK"]},
        {"description": "PV Power Balance",
            "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST,
            "options": ["PV input max current will be the max charged current",
                        "PV input max power will be the sum of the max charged power and loads power"]},
        {"description": "Max charging time for CV stage", "reading_type": ReadingType.TIME_MINUTES},
        {"description": "Operation Logic", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": ["Automatic mode", "On-line mode", "ECO mode"]},
    ],
    "test_responses": [
        b"(230.0 21.7 230.0 50.0 21.7 5000 4000 48.0 46.0 42.0 56.4 54.0 0 10 010 1 0 0 6 01 0 0 54.0 0 1\x6F\x7E\r",
        b"(120.0 25.0 120.0 60.0 25.0 3000 3000 48.0 46.0 44.0 58.4 54.4 2 30 060 1 2 0 9 01 0 7 54.0 0 1 000 0\x27\xc9\r",
        b"(230.0 13.0 230.0 50.0 13.0 3000 2400 24.0 23.0 21.0 28.2 27.0 0 30 50 0 2 1 - 01 1 0 26.0 0 0\xb9\xbd\r",
        b"(230.0 21.7 230.0 50.0 21.7 5000 5000 48.0 47.0 46.5 57.6 57.6 5 30 080 0 1 2 1 01 0 0 52.0 0 1\x03$\r",
        b"(230.0 21.7 230.0 50.0 21.7 5000 5000 48.0 47.0 46.5 57.6 57.6 9 30 080 0 1 2 1 01 0 0 52.0 0 1\x9c\x6f\r",
        b"(230.0 34.7 230.0 50.0 34.7 8000 8000 48.0 48.0 42.0 54.0 52.5 2 010 030 1 2 2 9 01 0 0 50.0 0 1 480 0 070\xd9`\r",
    ], }
QPIWS = {
    "name": "QPIWS",
    "description": "Get any active Warning Status flags",
    "category": CommandCategory.DATA,
    "result_type": ResultType.SINGLE,
    "reading_definitions": [
        {"description": "Warning", "reading_type": ReadingType.FLAGS,
            "response_type": ResponseType.FLAGS,
            "flags": [
                "PV loss warning",
                    "Inverter fault",
                    "Bus over fault",
                    "Bus under fault",
                    "Bus soft fail fault",
                    "Line fail warning",
                    "OPV short warning",
                    "Inverter voltage too low fault",
                    "Inverter voltage too high fault",
                    "Over temperature fault",
                    "Fan locked fault",
                    "Battery voltage to high fault",
                    "Battery low alarm warning",
                    "Reserved",
                    "Battery under shutdown warning",
                    "Battery derating warning",
                    "Overload fault",
                    "EEPROM fault",
                    "Inverter over current fault",
                    "Inverter soft fail fault",
                    "Self test fail fault",
                    "OP DC voltage over fault",
                    "Bat open fault",
                    "Current sensor fail fault",
                    "Battery short fault",
                    "Power limit warning",
                    "PV voltage high warning",
                    "MPPT overload fault",
                    "MPPT overload warning",
                    "Battery too low to charge warning",
                    "",
                    "Battery weak",
                    "Battery weak",
                    "Battery weak",
                    "",
                    "Battery equalisation warning"
            ]}
    ],
    "test_responses": [b"(00000100000000001000000000000000\x56\xA6\r", b"(000000000000000000000000000000000000<\x8e\r",], }
QPGS = {
    "name": "QPGS",
    "description": "Get the current values of various Parallel Status parameters",
    "help": " -- example: QPGS1 queries the values of various metrics from instance 1 of parallel setup Inverters (numbers from 0)",
    "category": CommandCategory.DATA,
    "result_type": ResultType.ORDERED,
    "reading_definitions": [
        {"description": "Parallel Instance Number", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": ["Not valid", "valid"]},
        {"description": "Serial Number", "reading_type": ReadingType.MESSAGE, "icon": "mdi:identifier", "response_type": ResponseType.BYTES},
        {"description": "Work Mode",
            "reading_type": ReadingType.MESSAGE, "device_class": "enum",
            "response_type": ResponseType.OPTION, "options": INVERTER_MODE_OPTIONS},
        {"description": "Fault Code",
            "reading_type": ReadingType.MESSAGE,
            "response_type": ResponseType.OPTION, "options": FAULT_CODE_OPTIONS},
        {"description": "Grid Voltage", "reading_type": ReadingType.VOLTS, "icon": "mdi:power-plug", "device_class": "voltage", "response_type": ResponseType.FLOAT},
        {"description": "Grid Frequency", "reading_type": ReadingType.FREQUENCY, "icon": "mdi:current-ac", "device_class": "frequency", "response_type": ResponseType.FLOAT},
        {"description": "AC Output Voltage", "reading_type": ReadingType.VOLTS, "icon": "mdi:power-plug", "device_class": "voltage", "response_type": ResponseType.FLOAT},
        {"description": "AC Output Frequency", "reading_type": ReadingType.FREQUENCY, "icon": "mdi:current-ac", "device_class": "frequency", "response_type": ResponseType.FLOAT},
        {"description": "AC Output Apparent Power", "reading_type": ReadingType.APPARENT_POWER, "icon": "mdi:power-plug", "device_class": "apparent_power",},
        {"description": "AC Output Active Power", "reading_type": ReadingType.WATTS, "icon": "mdi:power-plug", "device_class": "power", "state_class": "measurement"},
        {"description": "Load Percentage", "reading_type": ReadingType.PERCENTAGE, "icon": "mdi:brightness-percent"},
        {"description": "Battery Voltage", "reading_type": ReadingType.VOLTS, "icon": "mdi:battery-outline", "device_class": "voltage", "response_type": ResponseType.FLOAT},
        {"description": "Battery Charging Current", "reading_type": ReadingType.CURRENT, "icon": "mdi:current-dc", "device_class": "current"},
        {"description": "Battery Capacity", "reading_type": ReadingType.PERCENTAGE, "device_class": "battery"},
        {"description": "PV Input Voltage", "reading_type": ReadingType.VOLTS, "icon": "mdi:solar-power", "device_class": "voltage", "response_type": ResponseType.FLOAT},
        {"description": "Total Charging Current", "reading_type": ReadingType.CURRENT, "icon": "mdi:brightness-percent", "device_class": "current"},
        {"description": "Total AC Output Apparent Power", "reading_type": ReadingType.APPARENT_POWER, "icon": "mdi:power-plug", "device_class": "apparent_power"},
        {"description": "Total Output Active Power", "reading_type": ReadingType.WATTS, "icon": "mdi:power-plug", "device_class": "power", "state_class": "measurement"},
        {"description": "Total AC Output Percentage", "reading_type": ReadingType.PERCENTAGE, "icon": "mdi:brightness-percent"},
        {"description": "Inverter Status",
            "reading_type": ReadingType.FLAGS, 'component': 'binary_sensor',
            "response_type": ResponseType.FLAGS,
            "flags": [
                "Is SCC OK",
                "Is AC Charging",
                "Is SCC Charging",
                "Is Battery Over Voltage",
                "Is Battery Under Voltage",
                "Is Line Lost",
                "Is Load On",
                "Is Configuration Changed",
            ]},
        {"description": "Output Mode",
            "reading_type": ReadingType.MESSAGE, "device_class": "enum",
            "response_type": ResponseType.LIST,
            "options": OUTPUT_MODES},
        {"description": "Charger Source Priority",
            "reading_type": ReadingType.MESSAGE,
            "response_type": ResponseType.LIST,
            "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Max Charger Current", "reading_type": ReadingType.CURRENT, "device_class": "current"},
        {"description": "Max Charger Range", "reading_type": ReadingType.CURRENT, "device_class": "current"},
        {"description": "Max AC Charger Current", "reading_type": ReadingType.CURRENT, "device_class": "current"},
        {"description": "PV Input Current", "reading_type": ReadingType.CURRENT, "icon": "mdi:solar-power", "device_class": "power"},
        {"description": "Battery Discharge Current", "reading_type": ReadingType.CURRENT, "icon": "mdi:battery-negative", "device_class": "current"},
        {"description": "Unknown float", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.FLOAT},
        {"description": "Unknown flags?", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.BYTES},
    ],
    "test_responses": [
        b"(1 92931701100510 B 00 000.0 00.00 230.6 50.00 0275 0141 005 51.4 001 100 083.3 002 00574 00312 003 10100110 1 2 060 120 10 04 000\xcc#\r",
        b"(1 92912102100033 B 00 000.0 00.00 120.1 59.99 0048 0000 000 53.1 000 059 000.0 000 00154 00016 000 00000110 7 1 060 120 030 00 000 000.0 00\xe7c\r",
        b"(0 92932105105315 B 00 000.0 00.00 230.0 50.00 0989 0907 012 53.2 009 090 349.8 009 00989 00907 011 10100110 0 1 100 120 030 02 000 275.3 02i]\r",
        # b"QPGS0?\xda\r",
    ],
    "regex": "QPGS(\\d+)$", }
QFLAG = {
    "name": "QFLAG",
    "description": "Get the Status of various Inverter settings",
    "category": CommandCategory.SETTINGS,
    "result_type": ResultType.SINGLE,
    "reading_definitions": [
        {"description": "Device Status", "reading_type": ReadingType.MULTI_ENABLE_DISABLE,
            "response_type": ResponseType.ENABLE_DISABLE_FLAGS,
            "options": {
                "a": "Buzzer",
                "b": "Overload Bypass",
                "j": "Power Saving",
                "k": "LCD Reset to Default",
                "u": "Overload Restart",
                "v": "Over Temperature Restart",
                "x": "LCD Backlight",
                "y": "Primary Source Interrupt Alarm",
                "z": "Record Fault Code",
            }}
    ],
    "test_responses": [b"(EakxyDbjuvz\x2F\x29\r"], }
QMOD = {
    "name": "QMOD",
    "description": "Get the Inverter Mode",
    "category": CommandCategory.DATA,
    "result_type": ResultType.SINGLE,
    "reading_definitions": [
        {"description": "Device Mode", "reading_type": ReadingType.MESSAGE,
            "response_type": ResponseType.OPTION,
            "options": INVERTER_MODE_OPTIONS}
    ],
    "test_responses": [b"(S\xe5\xd9\r", b"(B\xe7\xc9\r",], }
Q1 = {
    "name": "Q1",
    "description": "Q1 query",
    "result_type": ResultType.ORDERED,
    "reading_definitions": [
        {"reading_type": ReadingType.TIME_SECONDS, "response_type": ResponseType.INT, "description": "Time until the end of absorb charging"},
        {"reading_type": ReadingType.TIME_SECONDS, "response_type": ResponseType.INT, "description": "Time until the end of float charging"},
        {"reading_type": ReadingType.MESSAGE, "response_type": ResponseType.OPTION, "description": "SCC Flag", "options": {"00": "SCC not communicating?", "01": "SCC is powered and communicating", "11": "I am probably decoding wrong, should this be a 3?"}},
        {"reading_type": ReadingType.MESSAGE, "response_type": ResponseType.OPTION, "description": "AllowSccOnFlag", "options": {"00": "SCC not allowed to charge", "01": "SCC allowed to charge"}},
        {"reading_type": ReadingType.CURRENT, "response_type": ResponseType.INT, "description": "ChargeAverageCurrent"},
        {"reading_type": ReadingType.TEMPERATURE, "response_type": ResponseType.INT, "description": "SCC PWM temperature", "device_class": "temperature"},
        {"reading_type": ReadingType.TEMPERATURE, "response_type": ResponseType.INT, "description": "Inverter temperature", "device_class": "temperature"},
        {"reading_type": ReadingType.TEMPERATURE, "response_type": ResponseType.INT, "description": "Battery temperature", "device_class": "temperature"},
        {"reading_type": ReadingType.TEMPERATURE, "response_type": ResponseType.INT, "description": "Transformer temperature", "device_class": "temperature"},
        {"reading_type": ReadingType.MESSAGE, "response_type": ResponseType.OPTION, "description": "Parallel Mode", "options": {"00": "New", "01": "Slave", "02": "Master"}},
        {"reading_type": ReadingType.MESSAGE, "response_type": ResponseType.OPTION, "description": "Fan lock status", "options": {"00": "Not locked", "01": "Locked"}},
        {"reading_type": ReadingType.MESSAGE, "response_type": ResponseType.BYTES, "description": "Not used"},
        {"reading_type": ReadingType.PERCENTAGE, "response_type": ResponseType.INT, "description": "Fan PWM speed"},
        {"reading_type": ReadingType.WATTS, "response_type": ResponseType.INT, "description": "SCC charge power", "icon": "mdi:solar-power", "device_class": "power"},
        {"reading_type": ReadingType.MESSAGE, "response_type": ResponseType.BYTES, "description": "Parallel Warning"},
        {"reading_type": ReadingType.FREQUENCY, "response_type": ResponseType.FLOAT, "description": "Sync frequency"},
        {
            "description": "Inverter charge status",
            "reading_type": ReadingType.MESSAGE,
            "response_type": ResponseType.OPTION,
            "options": {"10": "nocharging", "11": "bulk stage", "12": "absorb", "13": "float"},
            "icon": "mdi:book-open", },
    ],
    "test_responses": [b"(00000 00000 01 01 00 059 045 053 068 00 00 000 0040 0580 0000 50.00 139\xb9\r"], }
QBMS = {
        "name": "QBMS",
        "description": "Read lithium battery information",
        "category": CommandCategory.DATA,
        "result_type": ResultType.ORDERED,
        "reading_definitions": [
            {"description": "Battery is connected", "response_type": ResponseType.INV_BOOL},
            {"description": "Battery capacity from BMS", "reading_type": ReadingType.PERCENTAGE},
            {"description": "Battery charging is forced", "response_type": ResponseType.BOOL},
            {"description": "Battery discharge is enabled", "response_type": ResponseType.INV_BOOL},
            {"description": "Battery charge is enabled", "response_type": ResponseType.INV_BOOL},
            {"description": "Battery bulk charging voltage from BMS", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10"},
            {"description": "Battery float charging voltage from BMS", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10"},
            {"description": "Battery cut-off voltage from BMS", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10"},
            {"description": "Battery max charging current", "reading_type": ReadingType.CURRENT},
            {"description": "Battery max discharge current", "reading_type": ReadingType.CURRENT}],
        "test_responses": [
            b"(0 100 0 0 1 532 532 450 0000 0030\x0e\x5E\n",
        ], }
pi30_query_commands = [QPI, QID, QVFW, QVFW2, QBOOT, QDI, QMN, QGMN, QMCHGCR, QMUCHGCR, QOPM, QPIGS, QPIRI, QPIWS, QPGS, QFLAG, QMOD, Q1, QBMS]

# PI30 SETTER COMMANDS
F = {
    "name": "F",
    "description": "Set Device Output Frequency",
    "help": " -- examples: F50 (set output frequency to 50Hz) or F60 (set output frequency to 60Hz)",
    "regex": "F([56]0)$",
    }
MCHGC = {
    "name": "MCHGC",
    "description": "Set Max Charging Current (for parallel units)",
    "help": " -- examples: MCHGC040 (set unit 0 to max charging current of 40A), MCHGC160 (set unit 1 to max charging current of 60A)",
    "regex": "MCHGC(\\d\\d\\d)$",
    }
MNCHGC = {
    "name": "MNCHGC",
    "description": "Set Utility Max Charging Current (more than 100A) (for 4000/5000)",
    "help": " -- example: MNCHGC1120 (set unit 1 utility max charging current to 120A)",
    "regex": "MNCHGC(\\d\\d\\d\\d)$",
    }
MUCHGC = {
    "name": "MUCHGC",
    "description": "Set Utility Max Charging Current",
    "help": " -- example: MUCHGC130 (set unit 1 utility max charging current to 30A)",
    "regex": "MUCHGC(\\d\\d\\d)$",
    }
PBCV = {
    "name": "PBCV",
    "description": "Set Battery re-charge voltage",
    "help": " -- example PBCV44.0 - set re-charge voltage to 44V (12V unit: 11V/11.3V/11.5V/11.8V/12V/12.3V/12.5V/12.8V, 24V unit: 22V/22.5V/23V/23.5V/24V/24.5V/25V/25.5V, 48V unit: 44V/45V/46V/47V/48V/49V/50V/51V)",
    "regex": "PBCV(\\d\\d\\.\\d)$",
    }
PBDV = {
    "name": "PBDV",
    "description": "Set Battery re-discharge voltage",
    "help": " -- example PBDV48.0 - set re-discharge voltage to 48V (12V unit: 00.0V/12V/12.3V/12.5V/12.8V/13V/13.3V/13.5V/13.8V/14V/14.3V/14.5, 24V unit: 00.0V/24V/24.5V/25V/25.5V/26V/26.5V/27V/27.5V/28V/28.5V/29V, 48V unit: 00.0V/48V/49V/50V/51V/52V/53V/54V/55V/56V/57V/58V, 00.0V means battery is full(charging in float mode).)",
    "regex": "PBDV(\\d\\d\\.\\d)$",
    }
PBFT = {
    "name": "PBFT",
    "description": "Set Battery Float Charging Voltage",
    "help": " -- example PBFT58.0 - set battery float charging voltage to 58V (48.0 - 58.4V for 48V unit)",
    "regex": "PBFT(\\d\\d\\.\\d)$",
    }
PBT = {
    "name": "PBT",
    "description": "Set Battery Type",
    "help": " -- examples: PBT00 (set battery as AGM), PBT01 (set battery as FLOODED), PBT02 (set battery as USER)",
    "regex": "PBT(0[012])$",
    }
PCP = {
    "name": "PCP",
    "description": "Set Device Charger Priority",
    "help": " -- examples: PCP00 (set utility first), PCP01 (set solar first), PCP02 (HS only: set solar and utility), PCP03 (set solar only charging)",
    "regex": "PCP(0[0123])$",
    }
PCVV = {
    "name": "PCVV",
    "description": "Set Battery C.V. (constant voltage) charging voltage",
    "help": " -- example PCVV48.0 - set charging voltage to 48V (48.0 - 58.4V for 48V unit)",
    "regex": "PCVV(\\d\\d\\.\\d)$",
    }
PE = {
    "name": "PE",
    "description": "Set the enabled state of an Inverter setting",
    "help": " -- examples: PEa - enable a (buzzer) [a=buzzer, b=overload bypass, j=power saving, K=LCD go to default after 1min, u=overload restart, v=overtemp restart, x=backlight, y=alarm on primary source interrupt, z=fault code record]",
    "regex": "PE(.+)$",
    }
PD = {
    "name": "PD",
    "description": "Set the disabled state of an Inverter setting",
    "help": " -- examples: PDa - disable a (buzzer) [a=buzzer, b=overload bypass, j=power saving, K=LCD go to default after 1min, u=overload restart, v=overtemp restart, x=backlight, y=alarm on primary source interrupt, z=fault code record]",
    "regex": "PD(.+)$",
    }
PF = {
    "name": "PF",
    "description": "Set Control Parameters to Default Values",
    "help": " -- example PF (reset control parameters to defaults)",
    }
PGR = {
    "name": "PGR",
    "description": "Set Grid Working Range",
    "help": " -- examples: PCR00 (set device working range to appliance), PCR01 (set device working range to UPS)",
    "regex": "PGR(0[01])$",
    }
POP = {
    "name": "POP",
    "description": "Set Device Output Source Priority",
    "help": " -- examples: POP00 (set Utility > Solar > Battery), POP01 (set Solar > Utility > Battery), POP02 (set Solar > Battery > Utility)",
    "regex": "POP(0[012])$",
    }
POPLG = {
    "name": "POPLG",
    "description": "Set Device Operation Logic",
    "help": " -- examples: POPLG00 (set Auto mode), POPLG01 (set Online mode), POPLG02 (set ECO mode)",
    "regex": "POPLG(0[012])$",
    }
POPM = {
    "name": "POPM",
    "description": "Set Device Output Mode (for 4000/5000)",
    "help": " -- examples: POPM01 (set unit 0 to 1 - parallel output), POPM10 (set unit 1 to 0 - single machine output), POPM02 (set unit 0 to 2 - phase 1 of 3), POPM13 (set unit 1 to 3 - phase 2 of 3), POPM24 (set unit 2 to 4 - phase 3 of 3)",
    "regex": "POPM(\\d[01234])$",
    }
PPCP = {
    "name": "PPCP",
    "description": "Set Parallel Device Charger Priority (for 4000/5000)",
    "help": " -- examples: PPCP000 (set unit 1 to 00 - utility first), PPCP101 (set unit 1 to 01 - solar first), PPCP202 (set unit 2 to 02 - solar and utility), PPCP003 (set unit 0 to 03 - solar only charging)",
    "regex": "PPCP(\\d0[0123])$",
    }
PPVOKC = {
    "name": "PPVOKC",
    "description": "Set PV OK Condition",
    "help": " -- examples: PPVOKC0 (as long as one unit has connected PV, parallel system will consider PV OK), PPVOKC1 (only if all inverters have connected PV, parallel system will consider PV OK)",
    "regex": "PPVOKC([01])$",
    }
PSDV = {
    "name": "PSDV",
    "description": "Set Battery Cut-off Voltage",
    "help": " -- example PSDV40.0 - set battery cut-off voltage to 40V (40.0 - 48.0V for 48V unit)",
    "regex": "PSDV(\\d\\d\\.\\d)$",
    }
PSPB = {
    "name": "PSPB",
    "description": "Set Solar Power Balance",
    "help": " -- examples: PSPB0 (PV input max current will be the max charged current), PSPB1 (PV input max power will be the sum of the max charge power and loads power)",
    "regex": "PSPB([01])$",
    }
PBATCD = {
    "name": "PBATCD",
    "description": "Battery charge/discharge controlling command",
    "help": " -- examples: PBATCDxxx (please read description, use carefully)",
    "regex": "PBATCD([01][01][01])$",
    }
DAT = {
    "name": "DAT",
    "description": "Set Date Time",
    "help": " -- examples: DATYYYYMMDDHHMMSS (14 digits after DAT)",
    "regex": "DAT(\\d\\d\\d\\d\\d\\d\\d\\d\\d\\d\\d\\d\\d\\d)$",
    }
PBATMAXDISC = {
    "name": "PBATMAXDISC",
    "description": "Battery max discharge current",
    "help": " -- examples: PBATMAXDISCxxx (000- disable or 030-150A)",
    "regex": "PBATMAXDISC([01]\\d\\d)$",
    }
BTA = {
    "name": "BTA",
    "description": "Calibrate inverter battery voltage",
    "help": " -- examples: BTA-01 (reduce inverter reading by 0.05V), BTA+09 (increase inverter reading by 0.45V)",
    "regex": "BTA([-+]0\\d)$",
    }
PSAVE = {
    "name": "PSAVE",
    "description": "Save EEPROM changes",
    "help": " -- examples: PSAVE (save changes to eeprom)", 
    }
pi30_setter_commands = [F, MCHGC, MNCHGC, MUCHGC, PBCV, PBDV, PBFT, PBT, PCP, PCVV, PE, PD, PF, PGR, POP, POPLG, POPM, PPCP, PPVOKC, PSDV, PSPB, PBATCD, DAT, PBATMAXDISC, BTA, PSAVE]

# New QUERY Commands for MAX type inverters
QPIGS2 = {
        "name": "QPIGS2",
        "description": "Get the current values of various General Status parameters 2",
        "category": CommandCategory.DATA,
        "result_type": ResultType.ORDERED,
        "reading_definitions": [
            {"description": "PV2 Input Current",
                "reading_type": ReadingType.CURRENT, "icon": "mdi:solar-power", "device_class": "current", "state_class": "measurement",
                "response_type": ResponseType.FLOAT},
            {"description": "PV2 Input Voltage",
                "reading_type": ReadingType.VOLTS, "icon": "mdi:solar-power", "device_class": "voltage", "state_class": "measurement",
                "response_type": ResponseType.FLOAT},
            {"description": "PV2 Charging Power",
                "reading_type": ReadingType.WATTS, "icon": "mdi:solar-power", "device_class": "power", "state_class": "measurement",
                "response_type": ResponseType.INT},
        ],
        "test_responses": [
            b"(03.1 327.3 01026 \xc9\x8b\r",
        ],
    }
QSID = {
    "name": "QSID",
    "aliases": ["default", "get_id"],
    "description": "Get the Serial Number of the Inverter",
    "category": CommandCategory.INFO,
    "result_type": ResultType.SINGLE,
    "reading_definitions": [
        {"description": "Serial Number",
            "reading_type": ReadingType.MESSAGE, "icon": "mdi:identifier",
            "response_type": ResponseType.TEMPLATE_BYTES, "format_template" : "r[2:int(r[0:2])+2]"}],
    "test_responses": [b"(1492932105105335005535\x94\x0e\r", ],  
    }
QVFW3 = {
    "name": "QVFW3",
    "description": "Remote CPU firmware version inquiry",
    "result_type": ResultType.SINGLE,
    "reading_definitions": [
        {"description": "Remote CPU firmware version",
            "reading_type": ReadingType.MESSAGE, "icon": "mdi:identifier",
            "response_type": ResponseType.TEMPLATE_BYTES, "format_template": "r.removeprefix('VERFW:')"}],
    "test_responses": [b"(VERFW:00072.70\x53\xA7\r", ],
    }
VERFW = {
    "name": "VERFW",
    "description": "Get the Bluetooth Version",
    "result_type": ResultType.SINGLE,
    "reading_definitions": [
        {"description": "Bluetooth firmware version",
            "reading_type": ReadingType.MESSAGE, "icon": "mdi:identifier",
            "response_type": ResponseType.TEMPLATE_BYTES, "format_template": "r.removeprefix('VERFW:')"}],
    "test_responses": [b"(VERFW:00072.70\x53\xA7\r", ],
    }
QLED = {
    "name": "QLED",
    "description": "LED Status Parameters Inquiry",
    "result_type": ResultType.ORDERED,
    "reading_definitions": [
        {"description": "LED Enabled", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": ["Disabled", "Enabled"]},
        {"description": "LED Speed", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": ["Low", "Medium", "Fast"]},
        {"description": "LED Effect", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": ["Breathing", "Left Scrolling", "Solid", "Right Scrolling"]},
        {"description": "LED Brightness", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.INT},
        {"description": "LED Number of Colors", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.INT},
        {"description": "RGB", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.BYTES},
    ],
    "test_responses": [
        b"(1 1 2 5 3 148000211255255255000255255\xdaj\r",
    ],
    }
QCHPT = {
    "name": "QCHPT",
    "description": "Get Device Charger Source Priority Time Order",
    "result_type": ResultType.ORDERED,
    "reading_definitions": [
        {"description": "Charger Source Priority 00 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 01 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 02 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 03 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 04 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 05 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 06 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 07 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 08 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 09 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 10 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 11 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 12 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 13 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 14 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 15 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 16 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 17 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 18 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 19 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 20 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 21 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 22 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Charger Source Priority 23 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Device Charger Source Priority", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Selection of Charger Source Priority Order 1",
            "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Selection of Charger Source Priority Order 2",
            "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
        {"description": "Selection of Charger Source Priority Order 3",
            "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": CHARGER_SOURCE_PRIORITIES},
    ],
    "test_responses": [
        b"(3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 0 0 0\xd0\x8b\r",
    ],
    }
QOPPT = {
    "name": "QOPPT",
    "description": "Get Device Output Source Priority Time Order",
    "result_type": ResultType.ORDERED,
    "reading_definitions": [
        {"description": "Output Source Priority 00 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 01 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 02 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 03 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 04 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 05 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 06 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 07 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 08 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 09 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 10 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 11 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 12 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 13 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 14 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 15 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 16 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 17 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 18 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 19 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 20 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 21 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 22 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Output Source Priority 23 hours", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Device Output Source Priority", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Selection of Output Source Priority Order 1",
            "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Selection of Output Source Priority Order 2",
            "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
        {"description": "Selection of Output Source Priority Order 3",
            "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_SOURCE_PRIORITIES},
    ],
    "test_responses": [
        b"(2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 0 2 1>>\r",
    ],
    }
QLT = {
    "name": "QLT",
    "description": "Get Total Output Load Energy",
    "result_type": ResultType.SINGLE,
    "reading_definitions": [
        {"description": "Total Output Load Energy",
            "reading_type": ReadingType.WATT_HOURS, "icon": "mdi:counter", "device_class": "energy", "state_class": "total",
            "response_type": ResponseType.INT},
    ],
    "test_responses": [
        b"(00238800!J\r",
    ],
    }
QLY = {
    "name": "QLY",
    "description": "Get Yearly Output Load Energy",
    "result_type": ResultType.ORDERED,
    "reading_definitions": [
        {"description": "Output Load Energy for Year",
            "reading_type": ReadingType.WATT_HOURS, "icon": "mdi:counter", "device_class": "energy", "state_class": "total",
            "response_type": ResponseType.INT},
        {"description": "Year",
            "reading_type": ReadingType.YEAR,
            "response_type": ResponseType.INFO_FROM_COMMAND, "format_template": "int(cn[3:7])"},
    ],
    "test_responses": [
        b"(00238800!J\r",
    ],
    "regex": "QLY(\\d\\d\\d\\d)$",
    }
QLM = {
    "name": "QLM",
    "description": "Get Monthly Output Load Energy",
    "result_type": ResultType.ORDERED,
    "reading_definitions": [
        {"description": "Output Load Energy for Month",
            "reading_type": ReadingType.WATT_HOURS, "icon": "mdi:counter", "device_class": "energy", "state_class": "total",
            "response_type": ResponseType.INT},
        {"description": "Year",
            "reading_type": ReadingType.YEAR,
            "response_type": ResponseType.INFO_FROM_COMMAND, "format_template": "int(cn[3:7])"},
        {"description": "Month",
            "reading_type": ReadingType.MONTH,
            "response_type": ResponseType.INFO_FROM_COMMAND, "format_template": "calendar.month_name[int(cn[7:9])]"},
    ],
    "test_responses": [
        b"(00238800!J\r",
    ],
    "regex": "QLM(\\d\\d\\d\\d\\d\\d)$",
    }
QLD = {
    "name": "QLD",
    "description": "Get Daily Output Load Energy",
    "result_type": ResultType.ORDERED,
    "reading_definitions": [
        {"description": "Output Load Energy for Day",
            "reading_type": ReadingType.WATT_HOURS, "icon": "mdi:counter", "device_class": "energy", "state_class": "total",
            "response_type": ResponseType.INT},
        {"description": "Year",
            "reading_type": ReadingType.YEAR,
            "response_type": ResponseType.INFO_FROM_COMMAND, "format_template": "int(cn[3:7])"},
        {"description": "Month",
            "reading_type": ReadingType.MONTH,
            "response_type": ResponseType.INFO_FROM_COMMAND, "format_template": "calendar.month_name[int(cn[7:9])]"},
        {"description": "Day",
            "reading_type": ReadingType.DAY,
            "response_type": ResponseType.INFO_FROM_COMMAND, "format_template": "int(cn[9:11])"},
    ],
    "test_responses": [
        b"(00238800!J\r",
    ],
    "regex": "QLD(\\d\\d\\d\\d\\d\\d\\d\\d)$",
    }
QET = {
    "name": "QET",
    "description": "Get Total PV Generated Energy",
    "result_type": ResultType.SINGLE,
    "reading_definitions": [
        {"description": "Total PV Generated Energy",
            "reading_type": ReadingType.WATT_HOURS, "icon": "mdi:solar-power", "device_class": "energy", "state_class": "total_increasing",
            "response_type": ResponseType.INT}
    ],
    "test_responses": [
        b"(00238800!J\r",
    ],
    }
QEY = {
    "name": "QEY",
    "description": "Get Yearly PV Generated Energy",
    "result_type": ResultType.ORDERED,
    "reading_definitions": [
        {"description": "PV Generated Energy for Year",
            "reading_type": ReadingType.WATT_HOURS, "icon": "mdi:counter", "device_class": "energy", "state_class": "total_increasing",
            "response_type": ResponseType.INT},
        {"description": "Year",
            "reading_type": ReadingType.YEAR,
            "response_type": ResponseType.INFO_FROM_COMMAND, "format_template": "int(cn[3:])"},
    ],
    "test_responses": [
        b"(00238800!J\r",
    ],
    "regex": "QEY(\\d\\d\\d\\d)$",
    }
QEM = {
    "name": "QEM",
    "description": "Get Monthly PV Generated Energy",
    "result_type": ResultType.ORDERED,
    "reading_definitions": [
        {"description": "PV Generated Energy for Month",
            "reading_type": ReadingType.WATT_HOURS, "icon": "mdi:solar-power", "device_class": "energy", "state_class": "total_increasing",
            "response_type": ResponseType.INT},
        {"description": "Year",
            "reading_type": ReadingType.YEAR,
            "response_type": ResponseType.INFO_FROM_COMMAND, "format_template": "int(cn[3:7])"},
        {"description": "Month",
            "reading_type": ReadingType.MONTH,
            "response_type": ResponseType.INFO_FROM_COMMAND, "format_template": "calendar.month_name[int(cn[7:])]"},
    ],
    "test_responses": [
        b"(00238800!J\r",
    ],
    "regex": "QEM(\\d\\d\\d\\d\\d\\d)$",
    }
QED = {
    "name": "QED",
    "description": "Get Daily PV Generated Energy",
    "help": " -- display daily generated energy, format is QEDyyyymmdd",
    "result_type": ResultType.ORDERED,
    "reading_definitions": [
        {"description": "PV Generated Energy for Day",
            "reading_type": ReadingType.WATT_HOURS, "icon": "mdi:solar-power", "device_class": "energy", "state_class": "total_increasing",
            "response_type": ResponseType.INT},
        {"description": "Year",
            "reading_type": ReadingType.YEAR,
            "response_type": ResponseType.INFO_FROM_COMMAND, "format_template": "int(cn[3:7])"},
        {"description": "Month",
            "reading_type": ReadingType.MONTH,
            "response_type": ResponseType.INFO_FROM_COMMAND, "format_template": "calendar.month_name[int(cn[7:9])]"},
        {"description": "Day",
            "reading_type": ReadingType.DAY,
            "response_type": ResponseType.INFO_FROM_COMMAND, "format_template": "int(cn[9:11])"},
    ],
    "test_responses": [
        b"(00238800!J\r",
    ],
    "regex": "QED(\\d\\d\\d\\d\\d\\d\\d\\d)$",
    }
QT = {
    "name": "QT",
    "description": "Get the Device Time",
    "result_type": ResultType.SINGLE,
    "reading_definitions": [{"description": "Device Time", "reading_type": ReadingType.DATE_TIME, "response_type": ResponseType.BYTES}],
    "test_responses": [
        b"(20210726122606JF\r",
    ],
    }
QBEQI = {
    "name": "QBEQI",
    "description": "Get Battery Equalization Parameters and Status",
    "result_type": ResultType.ORDERED,
    "reading_definitions": [
        {"description": "Equalization Enabled", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": ["Disabled", "Enabled"]},
        {"description": "Equalization Time", "reading_type": ReadingType.TIME_MINUTES, "response_type": ResponseType.INT},
        {"description": "Equalization Period", "reading_type": ReadingType.TIME_DAYS, "response_type": ResponseType.INT},
        {"description": "Equalization Max Current", "reading_type": ReadingType.CURRENT, "response_type": ResponseType.INT},
        {"description": "Reserved1", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.BYTES},
        {"description": "Equalization Voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.FLOAT},
        {"description": "Reserved2", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.BYTES},
        {"description": "Equalization Over Time", "reading_type": ReadingType.TIME_MINUTES, "response_type": ResponseType.INT},
        {"description": "Equalization Active", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": ["Inactive", "Active"]},
        {"description": "Equalization Elasped Time", "reading_type": ReadingType.TIME_HOURS, "response_type": ResponseType.INT},
    ],
    "test_responses": [
        b"(1 030 030 080 021 55.40 224 030 0 0234y?\r",
    ],
    }
pi30max_additional_query_commands = [QPIGS2, QSID, QVFW3, VERFW, QCHPT, QOPPT, QLT, QLY, QLM, QLD, QET, QEY, QEM, QED, QT, QBEQI, QLED]

# New SETTER commands for MAX type inverters
PLEDB = {
    "name": "PLEDB",
    "description": "Set LED brightness",
    "help": " -- examples: PLEDB1 (set LED brightness low), PLEDB5 (set LED brightness normal), PLEDB9 (set LED brightness high)",
    "regex": "PLEDB([123456789])$",
    }
PLEDC ={
    "name": "PLEDC",
    "description": "Set LED color",
    "help": " -- examples: PLEDCnRRRGGGBBB (n: 1 line mode, 2 AVR mode, 3 battery mode)",
    "regex": "PLEDC([123]\\d\\d\\d\\d\\d\\d\\d\\d\\d)$",
    }
PLEDM = {
    "name": "PLEDM",
    "description": "Set LED effect",
    "help": " -- examples: PLEDM0 (set LED effect breathing), PLEDM2 (set LED effect solid), PLEDM3 (set LED right scrolling)",
    "regex": "PLEDM([0123])$",  # TODO: split into individual commands and add aliases
    }
PLEDS = {
    "name": "PLEDS",
    "description": "Set LED speed",
    "help": " -- examples: PLEDS0 (set LED speed low), PLEDS1 (set LED speed medium), PLEDS2 (set LED speed high)",
    "regex": "PLEDS([012])$",  # TODO: split into individual commands and add aliases
    }
PLEDT = {
    "name": "PLEDT",
    "description": "Set LED total number of colors",
    "help": " -- examples: PLEDT2 (set 2 LED colors), PLEDT3 (set 3 LED colors)",
    "regex": "PLEDT([123])$",
    }
PLEDE0 = {
    "name": "PLEDE0",
    "aliases": ["disable_led", "led=off", "set_led=off"],
    "description": "Disable LED function",
    "help": " -- examples: PLEDE0 (disable LED)",
    }
PLEDE1 = {
    "name": "PLEDE1",
    "aliases": ["enable_led", "led=on", "set_led=on"],
    "description": "Enable LED function",
    "help": " -- examples: PLEDE1 (enable LED)",
    }
pi30max_additional_setter_commands = [PLEDB, PLEDC, PLEDM, PLEDS, PLEDT, PLEDE0, PLEDE1]

# MAX / MST variation of QFLAGS options
MAX_QFLAG_OPTIONS = {
    "a": "Buzzer",
    "b": "Overload Bypass",
    "d": "Solar Feed to Grid",
    "k": "LCD Reset to Default",
    "u": "Overload Restart",
    "v": "Over Temperature Restart",
    "x": "LCD Backlight",
    "y": "Primary Source Interrupt Alarm",
    "z": "Record Fault Code"}
# MST variation of QPIGS2
MST_QPIGS2 = {
        "name": "QPIGS2",
        "description": "Get the current values of various General Status parameters 2",
        "category": CommandCategory.DATA,
        "result_type": ResultType.ORDERED,
        "reading_definitions": [
            {"description": "PV2 Input Current",
                "reading_type": ReadingType.CURRENT, "icon": "mdi:solar-power", "device_class": "current", "state_class": "measurement",
                "response_type": ResponseType.FLOAT},
            {"description": "PV2 Input Voltage",
                "reading_type": ReadingType.VOLTS, "icon": "mdi:solar-power", "device_class": "voltage", "state_class": "measurement",
                "response_type": ResponseType.FLOAT},
            {"description": "Battery voltage from SCC 2",
                "reading_type": ReadingType.VOLTS, "icon": "mdi:solar-power", "device_class": "voltage", "state_class": "measurement",
                "response_type": ResponseType.FLOAT},
            {"description": "PV2 Charging Power",
                "reading_type": ReadingType.WATTS, "icon": "mdi:solar-power", "device_class": "power", "state_class": "measurement",
                "response_type": ResponseType.INT},
            {"description": "Device status", "reading_type": ReadingType.MESSAGE,},
            {"description": "AC charging current",
                "reading_type": ReadingType.CURRENT, "icon": "mdi:transmission-tower-export", "device_class": "current", "state_class": "measurement",
                "response_type": ResponseType.FLOAT},
            {"description": "AC charging power",
                "reading_type": ReadingType.WATTS, "icon": "mdi:transmission-tower-export", "device_class": "power", "state_class": "measurement",
                "response_type": ResponseType.INT},
            {"description": "PV3 Input Current",
                "reading_type": ReadingType.CURRENT, "icon": "mdi:solar-power", "device_class": "current", "state_class": "measurement",
                "response_type": ResponseType.FLOAT},
            {"description": "PV3 Input Voltage",
                "reading_type": ReadingType.VOLTS, "icon": "mdi:solar-power", "device_class": "voltage", "state_class": "measurement",
                "response_type": ResponseType.FLOAT},
            {"description": "Battery voltage from SCC 3",
                "reading_type": ReadingType.VOLTS, "icon": "mdi:solar-power", "device_class": "voltage", "state_class": "measurement",
                "response_type": ResponseType.FLOAT},
            {"description": "PV3 Charging Power",
                "reading_type": ReadingType.WATTS, "icon": "mdi:solar-power", "device_class": "power", "state_class": "measurement",
                "response_type": ResponseType.INT},
            {"description": "PV total charging power",
                "reading_type": ReadingType.WATTS, "icon": "mdi:solar-power", "device_class": "power", "state_class": "measurement",
                "response_type": ResponseType.INT},
        ],
        "test_responses": [
            b"(03.1 327.3 52.3 123 1 1234 122 327.1 52.4 234 567 \x23\xc7\r",
        ], }


class PI30(AbstractProtocol):
    """ pi30 protocol handler """
    def __str__(self):
        return self.description

    def __init__(self, model=None) -> None:
        super().__init__(model=model)
        self.protocol_id = b"PI30"
        # self.add_command_definitions(QUERY_COMMANDS)
        self.add_command_definitions(command_definitions_list=pi30_query_commands)
        self.add_command_definitions(command_definitions_list=pi30_setter_commands, result_type=ResultType.ACK)
        self.add_supported_ports([PortType.SERIAL, PortType.USB])

        match model:
            case 'MAX':
                self.description = "PI30 protocol handler for LV6048MAX and similar inverters"
                self._update_to_max()
                self.check_definitions_count(expected=68)
            case "MST" | 'PIP4048MST':
                self.description = "PI30 protocol handler for PIP4048MST and similar inverters"
                self._update_to_max()
                # Update QPIGS2 to MST definition
                self.replace_command_definition("QPIGS2", MST_QPIGS2)
                self.check_definitions_count(expected=68)
            case _:
                self.description = "PI30 protocol handler"
                self.check_definitions_count(expected=45)

    def _update_to_max(self):
        """ function to update the PI30 command definitions to suit MAX type inverters """
        # Changes to PI30 for MAX type inverters
        # Add new commands
        self.add_command_definitions(command_definitions_list=pi30max_additional_query_commands)
        self.add_command_definitions(command_definitions_list=pi30max_additional_setter_commands, result_type=ResultType.ACK)
        # Remove PI30 commands that arent used on MAX inverters
        self.remove_command_definitions(["QVFW2"])
        # Remove QID ID aliases (replaced by QSID)
        self.command_definitions["QID"].aliases = None
        # Update QOPM options
        self.command_definitions["QOPM"].reading_definitions[0].options = PI30_OUTPUT_MODES
        # Update QFLAG options and change test_response to correspond to the different options
        self.command_definitions["QFLAG"].reading_definitions[0].options = MAX_QFLAG_OPTIONS
        self.command_definitions["QFLAG"].test_responses = [b"(EakxyDbduvz\x8d\x73\r"]
        # Update QDI reading definitions for MAX
        self.command_definitions["QDI"].reading_definitions[21].options = PI30_OUTPUT_MODES
        self.command_definitions["QDI"].reading_definitions[25] = ReadingDefinition.from_config({"description": "Max Charging Time at CV", "reading_type": ReadingType.TIME_MINUTES, "response_type": ResponseType.INT})
        self.command_definitions["QDI"].reading_definitions[26] = ReadingDefinition.from_config({"description": "Max Discharging current", "reading_type": ReadingType.CURRENT, "response_type": ResponseType.INT})
        # Update QPIGS reading definitions for MAX
        self.command_definitions["QPIGS"].reading_definitions[12].description = "PV1 Input Current"
        self.command_definitions["QPIGS"].reading_definitions[13].description = "PV1 Input Voltage"
        self.command_definitions["QPIGS"].reading_definitions[17] = ReadingDefinition.from_config({"description": "Battery Voltage Offset for Fans On (10mV)", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.INT})
        self.command_definitions["QPIGS"].reading_definitions[18] = ReadingDefinition.from_config({"description": "EEPROM Version", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.INT})
        self.command_definitions["QPIGS"].reading_definitions[19].description = "PV1 Input Power"
        self.command_definitions["QPIGS"].reading_definitions[21] = ReadingDefinition.from_config({"description": "Solar Feed to Grid", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": ["Disabled", "Enabled"]})
        self.command_definitions["QPIGS"].reading_definitions[22] = ReadingDefinition.from_config({"description": "Country", "reading_type": ReadingType.MESSAGE,
            "response_type": ResponseType.OPTION,
            "options": {
                "00": "India",
                "01": "Germany",
                "02": "South America",
            }})
        self.command_definitions["QPIGS"].reading_definitions[23] = ReadingDefinition.from_config({"description": "Solar Feed to Grid Power",
                "reading_type": ReadingType.WATTS, "icon": "mdi:solar-power", "device_class": "power", "state_class": "measurement"})
        self.command_definitions["QPIGS"].test_responses.append(b"(227.2 50.0 230.3 50.0 0829 0751 010 447 54.50 020 083 0054 02.7 323.6 00.00 00000 00010110 00 00 00879 010 1 02 123\x1c\x84\r")
        # Update QPGS reading definitions for MAX
        self.command_definitions["QPGS"].reading_definitions[3].options = FAULT_CODE_OPTIONS_PI30MAX
        self.command_definitions["QPGS"].reading_definitions[14].description = "PV1 Input Voltage"
        self.command_definitions["QPGS"].reading_definitions[20].options = PI30_OUTPUT_MODES
        self.command_definitions["QPGS"].reading_definitions[25].description = "PV1 Input Current"
        self.command_definitions["QPGS"].reading_definitions[27] = ReadingDefinition.from_config({"description": "PV2 Input Voltage", "reading_type": ReadingType.VOLTS, "icon": "mdi:solar-power", "device_class": "voltage", "response_type": ResponseType.FLOAT})
        self.command_definitions["QPGS"].reading_definitions[28] = ReadingDefinition.from_config({"description": "PV2 Input Current", "reading_type": ReadingType.CURRENT, "icon": "mdi:solar-power", "device_class": "current"})
        # Update QPIRI reading definitions for MAX
        self.command_definitions["QPIRI"].reading_definitions[27] = ReadingDefinition.from_config({"description": "Max discharging current", "reading_type": ReadingType.CURRENT, "icon": "mdi:current-ac", "device_class": "current"})
        self.command_definitions["QPIRI"].reading_definitions[21].options = PI30_OUTPUT_MODES

    def check_valid(self, response: str, command_definition: CommandDefinition = None) -> bool:
        """ check response is valid """
        log.debug("check valid for %s, definition: %s", response, command_definition)
        if response is None:
            raise InvalidResponse("Response is None")
        if len(response) <= 3:
            raise InvalidResponse("Response is too short")
        if response[0] != ord(b'('):
            raise InvalidResponse("Response missing start character '('")
        return True

    def check_crc(self, response: str, command_definition: CommandDefinition = None):
        """ crc check, needs override in protocol """
        log.debug("check crc for %s in pi30", response)
        # check crc matches the calculated one
        calc_crc_high, calc_crc_low = crc(response[:-3])
        crc_high, crc_low = response[-3], response[-2]
        if [calc_crc_high, calc_crc_low] != [crc_high, crc_low]:
            raise InvalidCRC(f"response has invalid CRC - got '\\x{crc_high:02x}\\x{crc_low:02x}', calculated '\\x{calc_crc_high:02x}\\x{calc_crc_low:02x}'", )
        log.debug("CRCs match")
        return True
