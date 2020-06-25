import logging
import re

from .protocol import AbstractProtocol

log = logging.getLogger('powermon')

COMMANDS = {
    'F': {
        "name": "F",
        "description": "Set Device Output Frequency",
        "help": " -- examples: F50 (set output frequency to 50Hz) or F60 (set output frequency to 60Hz)",
        "type": "SETTER",
        "response": [
            ["ack", "Command execution", {"NAK": "Failed", "ACK": "Successful"}],
        ],
        "test_responses": [
            b"(NAK\x73\x73\r",
            b"(ACK\x39\x20\r",
        ],
        "regex": "F([56]0)$",
    },
    'QPI': {
        "name": "QPI",
        "description": "Protocol ID inquiry",
        "help": " -- queries the device protocol ID. e.g. PI30 for HS series",
        "type": "QUERY",
        "response": [
            ["string", "Protocol ID", ""],
        ],
        "test_responses": [
            b"(PI30\x9a\x0b\r",
        ],
        "regex": "",
    },
    'QPIGS': {
        "name": "QPIGS",
        "description": "General Status Parameters inquiry",
        "help": " -- queries the value of various metrics from the Inverter",
        "type": "QUERY",
        "response": [
            ["float", "AC Input Voltage", "V"],
            ["float", "AC Input Frequency", "Hz"],
            ["float", "AC Output Voltage", "V"],
            ["float", "AC Output Frequency", "Hz"],
            ["int", "AC Output Apparent Power", "VA"],
            ["int", "AC Output Active Power", "W"],
            ["int", "AC Output Load", "%"],
            ["int", "BUS Voltage", "V"],
            ["float", "Battery Voltage", "V"],
            ["int", "Battery Charging Current", "A"],
            ["int", "Battery Capacity", "%"],
            ["int", "Inverter Heat Sink Temperature", "Deg_C"],
            ["float", "PV Input Current for Battery", "A"],
            ["float", "PV Input Voltage", "V"],
            ["float", "Battery Voltage from SCC", "V"],
            ["int", "Battery Discharge Current", "A"],
            ["flags", "Device Status", [
                "is_sbu_priority_version_added",
                "is_configuration_changed",
                "is_scc_firmware_updated",
                "is_load_on",
                "is_battery_voltage_to_steady_while_charging",
                "is_charging_on",
                "is_scc_charging_on",
                "is_ac_charging_on"]
             ],
            ["int", "RSV1", "A"],
            ["int", "RSV2", "A"],
            ["int", "PV Input Power", "W"],
            ["flags", "Device Status2", [
                "is_charging_to_float",
                "is_switched_on",
                "is_reserved"]
             ],
        ],
        "test_responses": [
            b"(000.0 00.0 230.0 49.9 0161 0119 003 460 57.50 012 100 0069 0014 103.8 57.45 00000 00110110 00 00 00856 010\x24\x8c\r",
        ],
        "regex": "",
    },
}

REGEX_COMMANDS = {
    'QPGS': {
        "name": "QPGS",
        "description": "Parallel Information inquiry",
        "help": " -- example: QPGS1 queries the values of various metrics from instance 1 of parallel setup Inverters (numbers from 0)",
        "type": "QUERY",
        "nosupports": ["LV5048"],
        "response": [
                ["option", "Parallel instance number", ["Not valid", "valid"]],
                ["string", "Serial number", ""],
                ["keyed", "Work mode", {"P": "Power On Mode",
                                        "S": "Standby Mode",
                                        "L": "Line Mode",
                                        "B": "Battery Mode",
                                        "F": "Fault Mode",
                                        "H": "Power Saving Mode"}],
                ["keyed", "Fault code", {"00": "No fault",
                                         "01": "Fan is locked",
                                         "02": "Over temperature",
                                         "03": "Battery voltage is too high",
                                         "04": "Battery voltage is too low",
                                         "05": "Output short circuited or Over temperature",
                                         "06": "Output voltage is too high",
                                         "07": "Over load time out",
                                         "08": "Bus voltage is too high",
                                         "09": "Bus soft start failed",
                                         "11": "Main relay failed",
                                         "51": "Over current inverter",
                                         "52": "Bus soft start failed",
                                         "53": "Inverter soft start failed",
                                         "54": "Self-test failed",
                                         "55": "Over DC voltage on output of inverter",
                                         "56": "Battery connection is open",
                                         "57": "Current sensor failed",
                                         "58": "Output voltage is too low",
                                         "60": "Inverter negative power",
                                         "71": "Parallel version different",
                                         "72": "Output circuit failed",
                                         "80": "CAN communication failed",
                                         "81": "Parallel host line lost",
                                         "82": "Parallel synchronized signal lost",
                                         "83": "Parallel battery voltage detect different",
                                         "84": "Parallel Line voltage or frequency detect different",
                                         "85": "Parallel Line input current unbalanced",
                                         "86": "Parallel output setting different"}],
                ["float", "Grid voltage", "V"],
                ["float", "Grid frequency", "Hz"],
                ["float", "AC output voltage", "V"],
                ["float", "AC output frequency", "Hz"],
                ["int", "AC output apparent power", "VA"],
                ["int", "AC output active power", "W"],
                ["int", "Load percentage", "%"],
                ["float", "Battery voltage", "V"],
                ["int", "Battery charging current", "A"],
                ["int", "Battery capacity", "%"],
                ["float", "PV Input Voltage", "V"],
                ["int", "Total charging current", "A"],
                ["int", "Total AC output apparent power", "VA"],
                ["int", "Total output active power", "W"],
                ["int", "Total AC output percentage", "%"],
                ["flags", "Inverter Status", [
                    "is_scc_ok",
                    "is_ac_charging",
                    "is_scc_charging",
                    "is_battery_over_voltage",
                    "is_battery_under_voltage",
                    "is_line_lost",
                    "is_load_on",
                    "is_configuration_changed"]],
                ["option", "Output mode", ["single machine",
                                           "parallel output",
                                           "Phase 1 of 3 phase output",
                                           "Phase 2 of 3 phase output",
                                           "Phase 3 of 3 phase output"]],
                ["option", "Charger source priority", ["Utility first", "Solar first", "Solar + Utility", "Solar only"]],
                ["int", "Max charger current", "A"],
                ["int", "Max charger range", "A"],
                ["int", "Max AC charger current", "A"],
                ["int", "PV input current", "A"],
                ["int", "Battery discharge current", "A"]
        ],
        "test_responses": [
            b"(1 92931701100510 B 00 000.0 00.00 230.6 50.00 0275 0141 005 51.4 001 100 083.3 002 00574 00312 003 10100110 1 2 060 120 10 04 000\xcc#\r",
        ],
        "regex": "QPGS(\\d)$",
    },
}


class pi30(AbstractProtocol):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self._protocol_id = b'PI30'
        log.info(f'Using protocol {self._protocol_id}')

    def set_command(self, command, show_raw=None) -> None:
        # Called from get_full_command
        self.__command = command
        self.__show_raw = show_raw
        self.__command_defn = self.get_command_defn(command)

    def get_command_defn(self, command) -> dict:
        log.debug(f'get_command_defn for: {command}')
        if self.__command is None:
            return None
        if command in COMMANDS:
            log.debug(f'Found command {self.__command} in protocol {self._protocol_id}')
            return COMMANDS[command]
        for _command in REGEX_COMMANDS:
            log.debug(f'Regex commands _command: {_command}')
            if 'regex' in REGEX_COMMANDS[_command] and REGEX_COMMANDS[_command]['regex']:
                _re = re.compile(REGEX_COMMANDS[_command]['regex'])
                match = _re.match(command)
                if match:
                    log.debug(f"Matched: {command} to: {REGEX_COMMANDS[_command]['name']} value: {match.group(1)}")
                    self.__command_value = match.group(1)
                    return REGEX_COMMANDS[_command]
        log.info(f'No command_defn found for {command}')
        return None

    def get_full_command(self, command, show_raw) -> bytes:
        self.set_command(command, show_raw)
        byte_cmd = bytes(self.__command, 'utf-8')
        # calculate the CRC
        crc_high, crc_low = self.crc(byte_cmd)
        # combine byte_cmd, CRC , return
        full_command = byte_cmd + bytes([crc_high, crc_low, 13])
        log.debug(f'full command: {full_command}')
        return full_command

    def decode(self, response) -> dict:
        msgs = {}
        log.debug(f'response passed to decode: {response}')
        # No response
        if response is None:
            log.info('No response')
            msgs['error'] = ['No response', '']
            return msgs

        # Raw response requested
        if self.__show_raw:
            log.debug(f'Protocol "{self._protocol_id}" raw response requested')
            msgs['raw_response'] = [response, '']
            return msgs

        # Check for a stored command definition
        if not self.__command_defn:
            # No definiution, so just return the data
            log.debug(f'No definition for command {self.__command}, raw response returned')
            # TODO: possibly return something better (maybe a dict with 'value_1 etc?')
            msgs['raw_response'] = [response[1:-3], '']
            msgs['error'] = [f'No definition for command {self.__command} in protocol {self._protocol_id}', '']
            return msgs

        # Decode response based on stored command definition
        # if not self.is_response_valid(response):
        #    log.info('Invalid response')
        #    msgs['error'] = ['Invalid response', '']
        #    msgs['response'] = [response, '']
        #    return msgs

        responses = response.split(b' ')
        # Trim leading '(' of first response
        responses[0] = responses[0][1:]
        # Remove CRC of last response
        responses[-1] = responses[-1][:-3]
        log.debug(f'trimmed and split responses: {responses}')

        for i, result in enumerate(responses):
            # decode result
            result = result.decode('utf-8')
            # Check if we are past the 'known' responses
            if (i >= len(self.__command_defn['response'])):
                resp_format = ['string', f'Unknown value in response {i}', '']
            else:
                resp_format = self.__command_defn['response'][i]

            key = '{}'.format(resp_format[1]).lower().replace(" ", "_")
            log.debug(f'result {result}, key {key}, resp_format {resp_format}')
            # Process results
            if (resp_format[0] == 'float'):
                msgs[key] = [float(result), resp_format[2]]
            elif (resp_format[0] == 'int'):
                msgs[key] = [int(result), resp_format[2]]
            elif (resp_format[0] == 'string'):
                msgs[key] = [result, resp_format[2]]
            elif (resp_format[0] == '10int'):
                msgs[key] = [float(result) / 10, resp_format[2]]
            # eg. ['option', 'Output source priority', ['Utility first', 'Solar first', 'SBU first']],
            elif (resp_format[0] == 'option'):
                msgs[key] = [resp_format[2][int(result)], '']
            # eg. ['keyed', 'Machine type', {'00': 'Grid tie', '01': 'Off Grid', '10': 'Hybrid'}],
            elif (resp_format[0] == 'keyed'):
                msgs[key] = [resp_format[2][result], '']
            # eg. ['flags', 'Device status', [ 'is_load_on', 'is_charging_on' ...
            elif (resp_format[0] == 'flags'):
                for j, flag in enumerate(result):
                    msgs[resp_format[2][j]] = [int(flag), 'True - 1/False - 0']
            # eg. ['stat_flags', 'Warning status', ['Reserved', 'Inver...
            elif (resp_format[0] == 'stat_flags'):
                output = ''
                for j, flag in enumerate(result):
                    if (flag == '1'):
                        output = ('{}\n\t- {}'.format(output,
                                                      resp_format[2][j]))
                msgs[key] = [output, '']
            # eg. ['enflags', 'Device Status', {'a': {'name': 'Buzzer', 'state': 'disabled'},
            elif (resp_format[0] == 'enflags'):
                # output = {}
                status = 'unknown'
                for item in result:
                    if (item == 'E'):
                        status = 'enabled'
                    elif (item == 'D'):
                        status = 'disabled'
                    else:
                        # output[resp_format[2][item]['name']] = status
                        msgs[resp_format[2][item]['name']] = [status, '']
                # msgs[key] = [output, '']
            elif self.__command_defn['type'] == 'SETTER':
                msgs[self.__command_defn['name']] = [result, '']
            else:
                msgs[i] = [result, '']
        return msgs
