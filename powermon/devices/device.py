import abc
import importlib
import logging

from powermon.io.hidrawio import HIDRawIO
from powermon.io.serialio import SerialIO
from powermon.io.testio import TestIO

log = logging.getLogger('powermon')


class AbstractDevice(metaclass=abc.ABCMeta):
    '''
    Abstract device class
    '''

    def __init__(self, *args, **kwargs):
        self._protocol = None
        self._protocol_class = None
        self._port = None

    def set_protocol(self, protocol=None):
        '''
        Set the protocol for this device
        '''
        log.debug(f'device.set_protocol with protocol {protocol}')
        if protocol is None:
            self._protocol = None
            self._protocol_class = None
            return
        protocol_id = protocol.lower()
        # Try to import the protocol module with the supplied name (may not exist)
        try:
            proto_module = importlib.import_module('powermon.protocols.' + protocol_id, '.')
        except ModuleNotFoundError:
            log.error(f'No module found for protocol {protocol_id}')
            self._protocol = None
            self._protocol_class = None
            return
        # Find the protocol class - classname must be the same as the protocol_id
        try:
            self._protocol_class = getattr(proto_module, protocol_id)
        except AttributeError:
            log.error(f'Module {proto_module} has no attribute {protocol_id}')
            self._protocol = None
            self._protocol_class = None
            return
        # Instantiate the class
        self._protocol = self._protocol_class('init_var', proto_keyword='value', second_keyword=123)

    def set_port(self, port=None):
        if port is None:
            self._port = None
            return
        # determine which IO type to use
        if TestIO.supports(port):
            log.info('Using testio for communications')
            self._port = TestIO()
        elif HIDRawIO.supports(port):
            log.info('Using hidrawio for communications')
            self._port = HIDRawIO(device_path=port)
        else:
            log.info('Using serialio for communications')
            self._port = SerialIO(serial_port=port, serial_baud=2400)
            print('hidraw not supported')
        # raise NotImplementedError

    @abc.abstractmethod
    def run_command(self, command=None, show_raw=False):
        raise NotImplementedError
