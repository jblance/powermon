""" pi30.py """
import logging

from powermon.commands.command_definition import CommandCategory, CommandDefinition
from powermon.commands.reading_definition import ReadingDefinition, ReadingType, ResponseType
from powermon.commands.result import ResultType
from powermon.libs.errors import InvalidCRC, InvalidResponse
from powermon.ports import PortType
from powermon.protocols.pi30 import PI30
from powermon.protocols.constants import (BATTERY_TYPES, CHARGER_SOURCE_PRIORITIES, FAULT_CODE_OPTIONS,
                                          FAULT_CODE_OPTIONS_PI30MAX, INVERTER_MODE_OPTIONS, OUTPUT_MODES,
                                          OUTPUT_SOURCE_PRIORITIES, PI30_OUTPUT_MODES)
from powermon.protocols.helpers import crc_pi30 as crc

log = logging.getLogger("pi30max")

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



class PI30MAX(PI30):
    """ pi30max protocol handler """
    def __str__(self):
        return self.description

    def __init__(self, model=None) -> None:
        super().__init__()
        self.protocol_id = "PI30MAX"
        self.description = "PI30 protocol handler for LV6048MAX and similar inverters"
        
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

        self.check_definitions_count(expected=68)
