import abc
import ctypes
import logging

log = logging.getLogger('powermon')


class AbstractProtocol(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_protocol_id(self):
        raise NotImplementedError

    @abc.abstractmethod
    def is_known_command(self, command):
        raise NotImplementedError

    @abc.abstractmethod
    def get_full_command(self, command):
        raise NotImplementedError

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
