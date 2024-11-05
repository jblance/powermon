""" powermon / protocols / pi18.py """
import logging

from powermon.commands.command import CommandType
from powermon.commands.command_definition import CommandDefinition
from powermon.commands.reading_definition import ReadingType, ResponseType
from powermon.commands.result import ResultType
from powermon.libs.errors import CommandDefinitionMissing, InvalidCRC, InvalidResponse
from powermon.ports import PortType
from powermon.protocols.abstractprotocol import AbstractProtocol
from powermon.protocols.helpers import crc_pi30 as crc
from powermon.protocols.pi30 import BATTERY_TYPE_LIST, OUTPUT_MODE_LIST

log = logging.getLogger("pi18")

SETTER_COMMANDS = {
    "POP": {
        "name": "POP",
        "command_type": CommandType.PI18_SETTER,
        "description": "Set Device Output Source Priority",
        "help": " -- examples: POP0 (set utility first), POP01 (set solar first)",
        "regex": "POP([01])$",
    },
    "PSP": {
        "name": "PSP",
        "command_type": CommandType.PI18_SETTER,
        "description": "Set Solar Power priority",
        "help": " -- examples: PSP0 (Battery-Load-Utility +AC Charge), PSP1 (Load-Battery-Utility)",
        "regex": "PSP([01])$",
    },
    "PEI": {
        "name": "PEI",
        "command_type": CommandType.PI18_SETTER,
        "description": "Set Machine type, enable: Grid-Tie",
        "help": " -- examples: PEI (enable Grid-Tie)",
    },
    "PDI": {
        "name": "PDI",
        "command_type": CommandType.PI18_SETTER,
        "description": "Set Machine type, disable: Grid-Tie",
        "help": " -- examples: PDI (disable Grid-Tie)",
    },
    "PCP": {
        "name": "PCP",
        "command_type": CommandType.PI18_SETTER,
        "description": "Set Device Charger Priority",
        "help": " -- examples: PCP0,1 (set unit 0 [0-9] to Solar and Utility)   PCP0,0 (set unit 0 to Solar first), PCP0,1 (set unit 0 to Solar and Utility), PCP0,2 (set unit 0 to solar only charging)",
        "regex": "PCP([0-9],[012])$",
    },
    "MCHGC": {
        "name": "MCHGC",
        "command_type": CommandType.PI18_SETTER,
        "description": "Set Battery Max Charging Current Solar + AC",
        "help": " -- examples: MCHGC0,040 (set unit 0 to max charging current of 40A), MCHGC1,060 (set unit 1 to max charging current of 60A) [010 020 030 040 050 060 070 080]",
        "regex": "MCHGC([0-9],0[1-8]0)$",
    },
    "MUCHGC": {
        "name": "MUCHGC",
        "command_type": CommandType.PI18_SETTER,
        "description": "Set Battery Max AC Charging Current",
        "help": " -- examples: MUCHGC0,040 (set unit 0 to max charging current of 40A), MUCHGC1,060 (set unit 1 to max charging current of 60A) [002 010 020 030 040 050 060 070 080]",
        "regex": "MUCHGC([0-9]),(002|0[1-8]0)$",
    },
    "PBT": {
        "name": "PBT",
        "command_type": CommandType.PI18_SETTER,
        "description": "Set Battery Type",
        "help": " -- examples: PBT0 (set battery as AGM), PBT1 (set battery as FLOODED), PBT2 (set battery as USER)",
        "regex": "PBT([012])$",
    },
    "MCHGV": {
        "name": "MCHGV",
        "command_type": CommandType.PI18_SETTER,
        "description": "Set Battery Bulk,Float Charging Voltages",
        "help": " -- example MCHGV552,540 - set battery charging voltage Bulk to 52.2V, float 54V (set Bulk Voltage [480~584] in 0.1V xxx, Float Voltage [480~584] in 0.1V yyy)",
        # Regex 48.0 - 58.4 Volt
        "regex": "MCHGV(4[8-9][0-9]|5[0-7][0-9]|58[0-5]),(4[8-9][0-9]|5[0-7][0-9]|58[0-4])$",
    },
    "PSDV": {
        "name": "PSDV",
        "command_type": CommandType.PI18_SETTER,
        "description": "Set Battery Cut-off Voltage",
        "help": " -- example PSDV400 - set battery cut-off voltage to 40V [400~480V] for 48V unit)",
        # Regex 40 to 48V
        "regex": "PSDV(4[0-7][0-9]|480)$",
    },
    "BUCD": {
        "name": "BUCD",
        "command_type": CommandType.PI18_SETTER,
        "description": "Set Battery Stop dis,charging when Grid is available",
        "help": " -- example BUCD440,480 - set Stop discharge Voltage [440~510] in 0.1V xxx, Stop Charge Voltage [000(Full) or 480~580] in 0.1V yyy",
        # Regex 44 to 51V, Full|48V to 58V
        "regex": "BUCD((4[4-9]0|5[0-1]0),(000|4[8-9]0|5[0-8]0))$",
    },
}

QUERY_COMMANDS = {
    "PI": {
        "name": "PI",
        "command_type": CommandType.PI18_QUERY,
        "description": "Protocol ID inquiry",
        "help": " -- queries the protocol ID",
        "result_type": ResultType.SINGLE,
        "reading_definitions": [
            {"description": "Protocol ID"},
        ],
        "test_responses": [
            b"^D00518m\xae\r"
        ]
    },
    "ID": {
        "name": "ID",
        "aliases": ["default", "get_id"],
        "command_type": CommandType.PI18_QUERY,
        "description": "Device Serial Number inquiry",
        "help": " -- queries the device serial number",
        "result_type": ResultType.SINGLE,
        "reading_definitions": [{"description": "Serial Number"}],
        "test_responses": [
            b"^D02514012345678901234567\r",
        ],
    },
    "ET": {
        "name": "ET",
        "command_type": CommandType.PI18_QUERY,
        "description": "Total PV Generated Energy Inquiry",
        "result_type": ResultType.SINGLE,
        "reading_definitions": [
            {"description": "Total PV Generated Energy", "reading_type": ReadingType.WATT_HOURS,
                "response_type": ResponseType.INT, "icon": "mdi:solar-power", "device_class": "energy", "state_class": "total"},
        ],
        "test_responses": [
            b""
        ],
    },
    "EY": {
        "name": "EY",
        "command_type": CommandType.PI18_QUERY,
        "description": "Yearly PV Generated Energy Inquiry",
        "result_type": ResultType.SINGLE,
        "reading_definitions": [
            {"description": "PV Generated Energy for Year", "reading_type": ReadingType.WATT_HOURS,
                "response_type": ResponseType.INT, "icon": "mdi:counter", "device_class": "energy", "state_class": "total"},
            {"description": "Year", "reading_type": ReadingType.YEAR,
                "response_type": ResponseType.INFO_FROM_COMMAND, "format_template": "int(cn[3:])"},
        ],
        "test_responses": [
            b"^D01105580051\x0b\x9f\r",
        ],
        "regex": "EY(\\d\\d\\d\\d)$",
    },
    "EM": {
        "name": "EM",
        "command_type": CommandType.PI18_QUERY,
        "description": "Monthly PV Generated Energy Inquiry",
        "result_type": ResultType.SINGLE,
        "reading_definitions": [
            {"description": "PV Generated Energy for Month", "reading_type": ReadingType.WATT_HOURS,
                "response_type": ResponseType.INT, "icon": "mdi:solar-power", "device_class": "energy", "state_class": "total"},
            {"description": "Year", "reading_type": ReadingType.YEAR,
                "response_type": ResponseType.INFO_FROM_COMMAND, "format_template": "int(cn[3:7])"},
            {"description": "Month", "reading_type": ReadingType.MONTH,
                "response_type": ResponseType.INFO_FROM_COMMAND, "format_template": "calendar.month_name[int(cn[7:])]"},
        ],
        "test_responses": [
            b"",
        ],
	"regex": "EM(\\d\\d\\d\\d\\d\\d)$",
    },
    "ED": {
        "name": "ED",
        "command_type": CommandType.PI18_QUERY,
        "description": "Daily PV Generated Energy Inquiry",
        "help": " -- display daily generated energy, format is QEDyyyymmdd",
        "result_type": ResultType.SINGLE,
        "reading_definitions": [
            {"description": "PV Generated Energy for Day", "reading_type": ReadingType.WATT_HOURS,
                "response_type": ResponseType.INT, "icon": "mdi:solar-power", "device_class": "energy", "state_class": "total"},
            {"description": "Year", "reading_type": ReadingType.YEAR,
                "response_type": ResponseType.INFO_FROM_COMMAND, "format_template": "int(cn[3:7])"},
            {"description": "Month", "reading_type": ReadingType.MONTH,
                "response_type": ResponseType.INFO_FROM_COMMAND, "format_template": "calendar.month_name[int(cn[7:9])]"},
            {"description": "Day", "reading_type": ReadingType.DAY,
                "response_type": ResponseType.INFO_FROM_COMMAND, "format_template": "int(cn[9:11])"},
        ],
        "test_responses": [
            b"(00238800!J\r",
        ],
        "regex": "ED(\\d\\d\\d\\d\\d\\d\\d\\d)$",
    },
    "PIRI": {
        "name": "PIRI",
        "command_type": CommandType.PI18_QUERY,
        "description": "Current Settings inquiry",
        "help": " -- queries the current settings from the Inverter",
        "result_type": ResultType.COMMA_DELIMITED,
        "reading_definitions": [
            {"description": "AC Input Voltage", "reading_type": ReadingType.VOLTS,
                "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10"},
            {"description": "AC Input Current", "reading_type": ReadingType.CURRENT,
                "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10"},
            {"description": "AC Output Voltage", "reading_type": ReadingType.VOLTS,
                "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10"},
            {"description": "AC Output Frequency", "reading_type": ReadingType.FREQUENCY,
                "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10"},
            {"description": "AC Output Current", "reading_type": ReadingType.CURRENT,
                 "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10"},
            {"description": "AC Output Apparent Power", "reading_type": ReadingType.APPARENT_POWER},
            {"description": "AC Output Active Power", "reading_type": ReadingType.WATTS},
            {"description": "Battery Voltage", "reading_type": ReadingType.VOLTS,
                 "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10"},
            {"description": "Battery re-charge Voltage", "reading_type": ReadingType.VOLTS,
                 "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10"},
            {"description": "Battery re-discharge Voltage", "reading_type": ReadingType.VOLTS,
                 "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10"},
            {"description": "Battery Under Voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10"},
            {"description": "Battery Bulk Charge Voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10"},
            {"description": "Battery Float Charge Voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10"},
            {"description": "Battery Type", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": BATTERY_TYPE_LIST},
            {"description": "Max AC Charging Current", "reading_type": ReadingType.CURRENT},
            {"description": "Max Charging Current", "reading_type": ReadingType.CURRENT},
            {"description": "Input Voltage Range", "response_type": ResponseType.LIST, "options": ["Appliance", "UPS"]},
            {"description": "Output Source Priority",
                "response_type": ResponseType.LIST, "options": ["Solar - Utility - Battery", "Solar - Battery - Utility"]},
            {"description": "Charger Source Priority",
                "response_type": ResponseType.LIST, "options": ["Solar First", "Solar + Utility", "Only solar charging permitted"]},
            {"description": "Max Parallel Units"},
            {"description": "Machine Type", "response_type": ResponseType.LIST, "options": ["Off Grid", "Grid Tie"]},
            {"description": "Topology", "response_type": ResponseType.LIST, "options": ["transformerless", "transformer"]},
            {"description": "Output Mode", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.LIST, "options": OUTPUT_MODE_LIST},
            {"description": "Solar power priority", "response_type": ResponseType.LIST, "options": ["Battery-Load-Utiliy + AC Charger", "Load-Battery-Utiliy"]},
            {"description": "MPPT strings"},
            {"description": "Unknown flags?", "response_type": ResponseType.STRING},
        ],
        "test_responses": [
            b"^D0882300,217,2300,500,217,5000,5000,480,480,530,440,570,570,2,10,070,1,1,1,9,0,0,0,0,1,00\xe1k\r",
        ]
    },
    "GS": {
        "name": "GS",
        "command_type": CommandType.PI18_QUERY,
        "description": "General Status Parameters inquiry",
        "result_type": ResultType.COMMA_DELIMITED,
        "reading_definitions": [
            {"description": "AC Input Voltage", "reading_type": ReadingType.VOLTS,
                "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10", "icon": "mdi:transmission-tower-export", "device_class": "voltage"},
            {"description": "AC Input Frequency", "reading_type": ReadingType.FREQUENCY,
                "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10", "icon": "mdi:current-ac", "device_class": "frequency"},
            {"description": "AC Output Voltage", "reading_type": ReadingType.VOLTS,
                "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10", "icon": "mdi:transmission-tower-export", "device_class": "voltage"},
            {"description": "AC Output Frequency", "reading_type": ReadingType.FREQUENCY,
                "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10", "icon": "mdi:current-ac", "device_class": "frequency"},
            {"description": "AC Output Apparent Power", "reading_type": ReadingType.APPARENT_POWER,
                "response_type": ResponseType.INT, "icon": "mdi:power-plug", "device_class": "apparent_power"},
            {"description": "AC Output Active Power", "reading_type": ReadingType.WATTS,
                "response_type": ResponseType.INT, "icon": "mdi:power-plug", "device_class": "power", "state_class": "measurement"},
            {"description": "AC Output Load", "reading_type": ReadingType.PERCENTAGE,
                "response_type": ResponseType.INT, "icon": "mdi:brightness-percent"},
            {"description": "Battery Voltage", "reading_type": ReadingType.VOLTS,
                "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10", "icon": "mdi:battery-outline", "device_class": "voltage"},
            {"description": "Battery Voltage from SCC", "reading_type": ReadingType.VOLTS,
                "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10", "icon": "mdi:battery-outline", "device_class": "voltage"},
            {"description": "Battery Voltage from SCC2", "reading_type": ReadingType.VOLTS,
                "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10", "icon": "mdi:battery-outline", "device_class": "voltage"},
            {"description": "Battery Discharge Current", "reading_type": ReadingType.CURRENT,
                "response_type": ResponseType.INT, "icon": "mdi:battery-negative", "device_class": "current"},
            {"description": "Battery Charging Current", "reading_type": ReadingType.CURRENT,
                "response_type": ResponseType.INT, "icon": "mdi:current-dc", "device_class": "current"},
            {"description": "Battery Capacity", "reading_type": ReadingType.PERCENTAGE,
                "response_type": ResponseType.INT, "icon": "mdi:brightness-percent", "device_class": "battery"},
            {"description": "Inverter heat sink temperature", "reading_type": ReadingType.TEMPERATURE,
                "response_type": ResponseType.INT, "icon": "mdi:details", "device_class": "temperature"},
            {"description": "MPPT1 charger temperature", "reading_type": ReadingType.TEMPERATURE,
                "response_type": ResponseType.INT, "icon": "mdi:details", "device_class": "temperature"},
            {"description": "MPPT2 charger temperature", "reading_type": ReadingType.TEMPERATURE,
                "response_type": ResponseType.INT, "icon": "mdi:details", "device_class": "temperature"},
            {"description": "MPPT1 Input Power", "reading_type": ReadingType.WATTS,
                "response_type": ResponseType.INT, "icon": "mdi:solar-power", "device_class": "power", "state_class": "measurement"},
            {"description": "MPPT2 Input Power", "reading_type": ReadingType.WATTS,
                "response_type": ResponseType.INT, "icon": "mdi:solar-power", "device_class": "power", "state_class": "measurement"},
            {"description": "MPPT1 Input Voltage", "reading_type": ReadingType.VOLTS,
                "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10", "icon": "mdi:solar-power", "device_class": "voltage"},
            {"description": "MPPT2 Input Voltage", "reading_type": ReadingType.VOLTS,
                "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10", "icon": "mdi:solar-power", "device_class": "voltage"},
            {"description": "Setting value configuration state", "reading_type": ReadingType.MESSAGE,
                "response_type": ResponseType.OPTION, 
                "options": {
                    "0": "Nothing changed",
                    "1": "Something changed",
                },
            },
            {"description": "MPPT1 charger status", "reading_type": ReadingType.MESSAGE,
                "response_type": ResponseType.OPTION,
                "options": {
                    "0": "abnormal",
                    "1": "normal but not charged",
                    "2": "charging",
                },
            },
            {"description": "MPPT2 charger status", "reading_type": ReadingType.MESSAGE,
                "response_type": ResponseType.OPTION,
                "options": {
                    "0": "abnormal",
                    "1": "normal but not charged",
                    "2": "charging",
                },
            },
            {"description": "Load connection", "reading_type": ReadingType.MESSAGE,
                "response_type": ResponseType.OPTION,
                "options": {
                    "0": "disconnect",
                    "1": "connect",
                },
            },
            {"description": "Battery power direction", "reading_type": ReadingType.MESSAGE,
                "response_type": ResponseType.OPTION,
                "options": {
                    "0": "donothing",
                    "1": "charge",
                    "2": "discharge",
                },
            },
            {"description": "DC/AC power direction", "reading_type": ReadingType.MESSAGE,
                "response_type": ResponseType.OPTION,
                "options": {
                    "0": "donothing",
                    "1": "AC-DC",
                    "2": "DC-AC",
                },
            },
            {"description": "Line power direction", "reading_type": ReadingType.MESSAGE, 
                "response_type": ResponseType.OPTION,
                "options": {
                    "0": "donothing",
                    "1": "input",
                    "2": "output",
                },
            },
            {"description": "Parallel instance number", "reading_type": ReadingType.MESSAGE,
                "response_type": ResponseType.LIST,
                "options": ["Not valid", "valid"],
            },

        ],
        "test_responses": [
            b"D1062232,499,2232,499,0971,0710,019,008,000,000,000,000,000,044,000,000,0520,0000,1941,0000,0,2,0,1,0,2,1,0\x09\x7b\r",
            b"^D1062232,499,2232,499,1406,1376,028,549,000,000,000,010,095,060,000,000,0082,0000,1604,0000,0,2,0,1,1,1,1,0D\x12\r",
        ],
    },
    "MOD": {
        "name": "MOD",
        "command_type": CommandType.PI18_QUERY,
        "description": "Mode inquiry",
        "result_type": ResultType.SINGLE,
        "reading_definitions": [
            {"description": "Device Mode", "reading_type": ReadingType.MESSAGE,
                "response_type": ResponseType.OPTION,
                "options": {
                    "00": "Power on",
                    "01": "Standby",
                    "02": "Bypass",
                    "03": "Battery",
                    "04": "Fault",
                    "05": "Hybrid mode(Line mode, Grid mode)",
                }
            },
        ],
        "test_responses": [
            b"^D00505\xd9\x9f\r",
        ],
    },
    "MCHGCR": {
        "name": "MCHGCR",
        "command_type": CommandType.PI18_QUERY,
        "description": "Max Charging Current Options inquiry",
        "help": " -- queries the maximum charging current setting of the Inverter",
        "result_type": ResultType.MULTIVALUED,
        "reading_definitions": [
            {"description": "Max Charging Current Options", "reading_type": ReadingType.MESSAGE_AMPS,
                 "response_type": ResponseType.STRING
            }
        ],
        "test_responses": [
            b"^D034010,020,030,040,050,060,070,080\x161\r",
        ],
    },
    "MUCHGCR": {
        "name": "MUCHGCR",
        "command_type": CommandType.PI18_QUERY,
        "description": "Max Utility Charging Current Options inquiry",
        "help": " -- queries the maximum utility charging current setting of the Inverter",
        "result_type": ResultType.MULTIVALUED,
        "reading_definitions": [
            {"reading_type": ReadingType.MESSAGE_AMPS, "description": "Max Utility Charging Current", "response_type": ResponseType.STRING}
        ],
        "test_responses": [
            b"^D038002,010,020,030,040,050,060,070,080\xd01\r"
        ],
    },
     "FLAG": {
        "name": "FLAG",
        "command_type": CommandType.PI18_QUERY,
        "description": "Query enable/disable flag status",
        "result_type": ResultType.COMMA_DELIMITED,
        "reading_definitions": [
            {"description": "Buzzer beep", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.ENABLED_BOOL},
            {"description": "Overload bypass function", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.ENABLED_BOOL},
            {"description": "Display back to default page", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.ENABLED_BOOL},
            {"description": "Overload restart", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.ENABLED_BOOL},
            {"description": "Over temperature restart", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.ENABLED_BOOL},
            {"description": "Backlight on", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.ENABLED_BOOL},
            {"description": "Alarm primary source interrupt", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.ENABLED_BOOL},
            {"description": "Fault code record", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.ENABLED_BOOL},
            {"description": "Reserved", "reading_type": ReadingType.MESSAGE},
        ],
        "test_responses": [
            b"^D0200,0,0,0,0,1,0,0,12\xc2\x39\r",
        ],
    },
    "VFW": {
        "name": "VFW",
        "description": "Device CPU version inquiry",
        "command_type": CommandType.PI18_QUERY,
        "result_type": ResultType.COMMA_DELIMITED,
        "reading_definitions": [
            {"description": "Main CPU Version", "reading_type": ReadingType.MESSAGE},
            {"description": "Slave 1 CPU Version", "reading_type": ReadingType.MESSAGE},
            {"description": "Slave 2 CPU Version", "reading_type": ReadingType.MESSAGE},
        ],
        "test_responses": [
            b"^D02005220,00000,00000\x3e\xf8\r",
        ],
    },
}

COMMANDS_TO_REMOVE = []


class PI18(AbstractProtocol):
    """ pi18 protocol handler """
    def __str__(self):
        return "PI18 protocol handler"

    def __init__(self) -> None:
        super().__init__()
        self.protocol_id = b"PI18"
        self.add_command_definitions(QUERY_COMMANDS)
        self.add_command_definitions(SETTER_COMMANDS, result_type=ResultType.PI18_ACK)
        self.remove_command_definitions(COMMANDS_TO_REMOVE)
        self.check_definitions_count(expected=24) # Count of all Commands
        self.add_supported_ports([PortType.SERIAL, PortType.USB])

    def check_crc(self, response: str, command_definition: CommandDefinition = None):
        """ crc check, override for now """
        log.debug("check crc for %s in pi18", response)
        if response.startswith(b"^D") or response.startswith(b"^1") or response.startswith(b"^0"):
            # get response CRC
            data_to_check = response[:-3]
            crc_high, crc_low = crc(data_to_check)
            # print(crc_high, crc_low)
            # print(response[-3], response[-2])
            if (crc_high, crc_low) == (response[-3], response[-2]):
                return True
            else:
                log.info("PI18 response check_crc doesnt match calc (%x, %x), got (%x, %x)", crc_high, crc_low, response[-3], response[-2])
                raise InvalidCRC(f"PI18 response check_crc doesnt match calc ({crc_high:02x}, {crc_low:02x}), got ({response[-3]:02x}, {response[-2]:02x})")
        else:
            log.info("PI18 response doesnt start with ^D - check_crc fails")
            raise InvalidResponse("PI18 response starts with invalid character - crc check fails")

        log.info("PI18 response check_crc fall through")
        return False

    def trim_response(self, response: str, command_definition: CommandDefinition = None) -> str:
        """ Remove extra characters from response """
        log.debug("trim %s, definition: %s", response, command_definition)
        if response.startswith(b"^D"):
            # trim ^Dxxx where xxx is data length
            response = response[5:]
        if response.endswith(b'\r'):
            # has checksum, so trim last 3 chars
            response = response[:-3]
        if response.startswith(b'('):
            # pi30 style response
            response = response[1:]
        # if response.startswith(b'^1') or response.startswith(b'^0'):
        #     # ACK / NACK response
        #     response = response[1:]
        return response

    def get_full_command(self, command: str) -> bytes:
        """ generate the full command including prefix, crc and \n as needed """
        log.info("Using protocol: %s with %i commands", self.protocol_id, len(self.command_definitions))
        command_defn = self.get_command_definition(command)

        # raise exception if no command definition is found
        if command_defn is None:
            raise CommandDefinitionMissing(f"No definition found in PI18 for {command}")

        # full command is ^PlllCCCcrc\n or ^SlllCCCcrc\n
        # lll = length of all except ^Dlll
        # CCC = command
        # crc = 2 bytes
        length = len(command) + 3
        # Determine prefix
        match command_defn.command_type:
            case CommandType.PI18_QUERY:
                prefix = "^P"
            case CommandType.PI18_SETTER:
                prefix = "^S"
            case _:
                # edge case / default PI30 command / maybe this should raise an error
                prefix = "("
        full_command = bytes(f"{prefix}{length:#03d}{command}", "utf-8")
        crc_high, crc_low = crc(full_command)
        full_command += bytes([crc_high, crc_low, 13])

        log.debug("full command: %s", full_command)
        return full_command
