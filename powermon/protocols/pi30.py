import logging

from .protocol import AbstractProtocol

log = logging.getLogger('powermon')

COMMANDS = ['QPI', 'QPIGS']


class pi30(AbstractProtocol):
    def __init__(self, *args, **kwargs) -> None:
        self._protocol_id = 'PI30'
        log.info(f'Using protocol {self._protocol_id}')

    def get_protocol_id(self):
        return self._protocol_id

    def is_known_command(self, command) -> bool:
        if command in COMMANDS:
            return True
        else:
            return False

    def get_full_command(self, command) -> bytes:
        byte_cmd = bytes(command, 'utf-8')
        # calculate the CRC
        crc_high, crc_low = self.crc(byte_cmd)
        # combine byte_cmd, CRC , return
        full_command = byte_cmd + bytes([crc_high, crc_low, 13])
        log.debug('full command: %s', full_command)
        return full_command
