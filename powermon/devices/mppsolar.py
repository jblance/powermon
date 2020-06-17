import logging

from .device import AbstractDevice
from ..exceptions import PowerMonUnknownProtocol

log = logging.getLogger('powermon')


class mppsolar(AbstractDevice):
    def __init__(self, *args, **kwargs) -> None:
        self._name = kwargs['name']
        self.set_port(port=kwargs['port'])
        self.set_protocol(protocol=kwargs['protocol'])
        log.debug(f'mppsolar __init__ name {self._name}, port {self._port}, protocol {self._protocol}')
        log.debug(f'mppsolar __init__ args {args}')
        log.debug(f'mppsolar __init__ kwargs {kwargs}')

    def set_protocol(self, protocol=None):
        log.debug(f'mppsolar.set_protocol protocol={protocol}')
        super().set_protocol(protocol)
        if self._protocol is None:
            log.error('Error setting protocol')
            return

        crc_high, crc_low = self._protocol.crc('test')
        log.debug(f'test {crc_high:#04x} {crc_low:#04x}')

    def run_command(self, command):
        '''
        mpp-solar specific method of running a 'raw' command, e.g. QPI or PI
        '''
        log.info(f'Running command {command}')
        # Have command like QPI or PI
        # validate protocol first
        if self._protocol is None:
            raise PowerMonUnknownProtocol('Attempted to run command with no protocol defined')
        # do we check it is a valid/known command?
        if self._protocol.is_known_command(command):
            log.info(f'{command} is a known command for protocol {self._protocol.get_protocol_id()}')
            full_command = self._protocol.get_full_command(command)
            log.info(f'full command {full_command} for command {command}')
            # self._port.write(full_command)
            response = self._port.read(10)
            _response = response.decode('utf-8')
            print(f'response {response}')
            print(f'_response {_response[-3:]}')
        else:
            log.info(f'{command} is NOT a known command for protocol {self._protocol.get_protocol_id()}')
        # need 'full' command string
        # write full command to io and get response
        # do we check for valid response
        # process response
        # output response
