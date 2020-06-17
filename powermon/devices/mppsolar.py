import logging

from .device import AbstractDevice

log = logging.getLogger('powermon')


class mppsolar(AbstractDevice):
    def __init__(self, *args, **kwargs) -> None:
        self._name = kwargs['name']
        self._port = self.set_communications(communications=kwargs['port'])
        self._protocol = self.set_protocol(protocol=kwargs['protocol'])
        print(f'name {self._name}, port {self._port}')
        # print(args)
        # print(kwargs)

    def set_protocol(self, protocol=None):
        super().set_protocol(protocol)
        if self._protocol is None:
            log.error('Error setting protocol')
            return

        crc_high, crc_low = self._protocol.crc('test')
        print(f'test {crc_high:#04x} {crc_low:#04x}')

    def run_command(self, command):
        print(f'Running command {command}')
