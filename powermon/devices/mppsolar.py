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
        # TODO: implement protocol determiniation??
        # validate protocol first
        if self._protocol is None:
            raise PowerMonUnknownProtocol('Attempted to run command with no protocol defined')

        full_command = self._protocol.get_full_command(command)
        log.info(f'full command {full_command} for command {command}')
        if self._port is None:
            log.error(f'No communications port defined - unable to run command {command}')
            # TODO: determine what to return when unable to run command
            return
        # Send the full command via the communications port
        # self._port.write(full_command)
        # Get the response from the communications port
        # TODO: sort async port read
        response = self._port.read(10)
        _response = response.decode('utf-8')
        log.debug(f'response {response}')
        log.debug(f'_response {_response}')
        # check it is a valid/known command?
        if not self._protocol.is_known_command(command):
            log.info(f'{command} is NOT a known command for protocol {self._protocol.get_protocol_id()}')
            # TODO: determine what to do when we run an unknown command
            return
        log.info(f'{command} is a known command for protocol {self._protocol.get_protocol_id()}')
        # TODO: do we check for valid response
        # TODO: process response
        # TODO: output response
