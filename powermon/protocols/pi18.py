import logging
import re

from .protocol import AbstractProtocol
from .pi30 import COMMANDS

log = logging.getLogger('powermon')


class pi18(AbstractProtocol):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self._protocol_id = b'PI18'
        log.info(f'Using protocol {self._protocol_id}')
        print(COMMANDS)

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
        for _command in COMMANDS:
            if 'regex' in COMMANDS[_command] and COMMANDS[_command]['regex']:
                log.debug(f'Regex commands _command: {_command}')
                _re = re.compile(COMMANDS[_command]['regex'])
                match = _re.match(command)
                if match:
                    log.debug(f"Matched: {command} to: {COMMANDS[_command]['name']} value: {match.group(1)}")
                    self.__command_value = match.group(1)
                    return COMMANDS[_command]
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
            msgs['ERROR'] = ['No response', '']
            return msgs

        # Raw response requested
        if self.__show_raw:
            log.debug(f'Protocol "{self._protocol_id}" raw response requested')
            msgs['raw_response'] = [response, '']
            return msgs

        # Check for a stored command definition
        if not self.__command_defn:
            # No definiution, so just return the data
            len_command_defn = 0
            log.debug(f'No definition for command {self.__command}, raw response returned')
            msgs['ERROR'] = [f'No definition for command {self.__command} in protocol {self._protocol_id}', '']
        else:
            len_command_defn = len(self.__command_defn['response'])
        # Decode response based on stored command definition
        # if not self.is_response_valid(response):
        #    log.info('Invalid response')
        #    msgs['ERROR'] = ['Invalid response', '']
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
            if i >= len_command_defn:
                resp_format = ['string', f'Unknown value in response {i}', '']
            else:
                resp_format = self.__command_defn['response'][i]

            key = '{}'.format(resp_format[1]).lower().replace(" ", "_")
            # log.debug(f'result {result}, key {key}, resp_format {resp_format}')
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
