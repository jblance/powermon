import logging

from .device import AbstractDevice

log = logging.getLogger('powermon')


class mppsolar(AbstractDevice):
    def __init__(self, *args, **kwargs) -> None:
        self._name = kwargs['name']
        self.set_port(port=kwargs['port'])
        self.set_protocol(protocol=kwargs['protocol'])
        log.debug(f'mppsolar __init__ name {self._name}, port {self._port}, protocol {self._protocol}')
        log.debug(f'mppsolar __init__ args {args}')
        log.debug(f'mppsolar __init__ kwargs {kwargs}')

    def set_protocol(self, protocol=None) -> None:
        log.debug(f'mppsolar.set_protocol protocol={protocol}')
        super().set_protocol(protocol)
        if self._protocol is None:
            log.error('Error setting protocol')
            return

        crc_high, crc_low = self._protocol.crc('test')
        log.debug(f'test {crc_high:#04x} {crc_low:#04x}')

    def run_command(self, command, show_raw=False) -> dict:
        '''
        mpp-solar specific method of running a 'raw' command, e.g. QPI or PI
        '''
        log.info(f'Running command {command}')
        # TODO: implement protocol determiniation??
        if self._protocol is None:
            log.error('Attempted to run command with no protocol defined')
            return {'error': 'Attempted to run command with no protocol defined'}
        if self._port is None:
            log.error(f'No communications port defined - unable to run command {command}')
            return {'error': f'No communications port defined - unable to run command {command}'}

        response = self._port.send_and_receive(command, show_raw, self._protocol)
        log.debug(f'Response {response}')

        # full_command = self._protocol.get_full_command(command, show_raw)
        # log.info(f'full command {full_command} for command {command}')
        # Send the full command via the communications port
        # self._port.write(full_command)
        # Get the response from the communications port
        # TODO: sort async port read
        # response = self._port.read(10)
        # decoded_response = self._protocol.decode(response)
        # _response = response.decode('utf-8')
        # log.info(f'Raw response {response}')
        # log.info(f'Decoded response {decoded_response}')
        return response
