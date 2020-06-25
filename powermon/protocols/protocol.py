import abc
import ctypes
import logging

log = logging.getLogger('powermon')


class AbstractProtocol(metaclass=abc.ABCMeta):
    def __init(self, *args, **kwargs) -> None:
        self.__command = None
        self.__command_dict = None
        self.__show_raw = None

    def get_protocol_id(self) -> bytes:
        return self._protocol_id

    @abc.abstractmethod
    def get_full_command(self, command, show_raw):
        raise NotImplementedError

    @abc.abstractmethod
    def get_command_defn(self, command) -> dict:
        raise NotImplementedError

    def get_responses(self, response):
        responses = response.split(b' ')
        # Trim leading '(' of first response
        responses[0] = responses[0][1:]
        # Remove CRC of last response
        responses[-1] = responses[-1][:-3]

    def decode(self, response) -> dict:
        raise NotImplementedError
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

        responses = self.get_responses(response)

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

    def crc(self, data_bytes):
        """
        Calculates CRC for supplied data_bytes
        """
        # assert type(byte_cmd) == bytes
        log.debug('Calculating CRC for %s', data_bytes)

        crc = 0
        da = 0
        crc_ta = [0x0000, 0x1021, 0x2042, 0x3063,
                  0x4084, 0x50a5, 0x60c6, 0x70e7,
                  0x8108, 0x9129, 0xa14a, 0xb16b,
                  0xc18c, 0xd1ad, 0xe1ce, 0xf1ef]

        for c in data_bytes:
            # todo fix spaces
            if c == ' ':
                continue
            # log.debug('Encoding %s', c)
            # todo fix response for older python
            if type(c) == str:
                c = ord(c)
            t_da = ctypes.c_uint8(crc >> 8)
            da = t_da.value >> 4
            crc <<= 4
            index = da ^ (c >> 4)
            crc ^= crc_ta[index]
            t_da = ctypes.c_uint8(crc >> 8)
            da = t_da.value >> 4
            crc <<= 4
            index = da ^ (c & 0x0f)
            crc ^= crc_ta[index]

        crc_low = ctypes.c_uint8(crc).value
        crc_high = ctypes.c_uint8(crc >> 8).value

        if (crc_low == 0x28 or crc_low == 0x0d or crc_low == 0x0a):
            crc_low += 1
        if (crc_high == 0x28 or crc_high == 0x0d or crc_high == 0x0a):
            crc_high += 1

        crc = crc_high << 8
        crc += crc_low

        log.debug(f'Generated CRC {crc_high:#04x} {crc_low:#04x} {crc:#06x}')
        return [crc_high, crc_low]
