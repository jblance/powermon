import abc
import importlib
import logging

log = logging.getLogger('powermon')

SERIAL_TYPE_TEST = 1
SERIAL_TYPE_USB = 2
SERIAL_TYPE_ESP32 = 4
SERIAL_TYPE_SERIAL = 8


class AbstractDevice(metaclass=abc.ABCMeta):
    '''
    Abstract device class
    '''
    @classmethod
    def is_directusb_device(serial_device):
        """
        Determine if this instance is using direct USB connection
        (instead of a serial connection)
        """
        if not serial_device:
            return False
        if 'hidraw' in serial_device:
            log.debug("Device matches hidraw")
            return True
        if 'mppsolar' in serial_device:
            log.debug("Device matches mppsolar")
            return True
        return False

    @classmethod
    def is_ESP32_device(serial_device):
        return 'esp' in serial_device.lower()

    @classmethod
    def get_port_type(self, port):
        if port == 'TEST':
            return SERIAL_TYPE_TEST
        elif self.is_directusb_device(port):
            return SERIAL_TYPE_USB
        elif self.is_ESP32_device(port):
            return SERIAL_TYPE_ESP32
        else:
            return SERIAL_TYPE_SERIAL

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
        port_type = self.get_port_type(port)
        if port_type == SERIAL_TYPE_TEST:
            log.info('Using testio for communications')
            from powermon.io.testio import TestIO
            self._port = TestIO()
        elif port_type == SERIAL_TYPE_USB:
            log.info('Using hidrawio for communications')
            from powermon.io.hidrawio import HIDRawIO
            self._port = HIDRawIO(device_path=port)
        elif port_type == SERIAL_TYPE_ESP32:
            log.info('Using esp32io for communications')
            log.critical('ESP23IO Not implemented yet')
        elif port_type == SERIAL_TYPE_SERIAL:
            log.info('Using serialio for communications')
            from powermon.io.serialio import SerialIO
            self._port = SerialIO(serial_port=port, serial_baud=2400)
        else:
            self._port = None

    @abc.abstractmethod
    def run_command(self, command=None, show_raw=False):
        raise NotImplementedError
