""" test_sbleport.py """
# import asyncio
from unittest import TestCase
from unittest.mock import patch

# from powermon.commands.command import Command
from powermon.libs.errors import PowermonProtocolError
from powermon.ports.bleport import BlePort
from powermon.protocols.daly import Daly
from powermon.protocols.pi30 import PI30 as UnsupportedProto

proto = Daly()

class TestBlePort(TestCase):
    """ unit tests for the serial port object and functionality """
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.port = None
        self.command = None

    def test_protocol_without_ble_handles(self):
        """test if correct exception raised if attempting to create a BLEPort without the handles defined in the protocol"""

        with patch.object(proto, 'notifier_handle', 0):
            self.assertRaises(PowermonProtocolError, BlePort, mac='00:00:00:00:00', protocol=proto)

    def test_protocol_not_supported(self):
        """ test correct exception is raised if port is configured with an unsupported protocol"""
        unsupported_proto = UnsupportedProto()
        # BlePort(mac='00:00:00:00:00', protocol=unsupported_proto)
        self.assertRaises(PowermonProtocolError, BlePort, mac='00:00:00:00:00', protocol=unsupported_proto)

    def test_protocol_supported(self):
        """ test xxx if port is configured with a supported protocol"""
        # unsupported_proto = UnsupportedProto()
        bleport = BlePort(mac='00:00:00:00:00', protocol=proto)
        # print(isinstance(bleport, BlePort))
        self.assertIsInstance(bleport, BlePort)

    # def test_is_connected_when_port_is_open(self):
    #     """
    #     Test if is_connected() method return True if serial_port is not None and is_open is True
    #     """
    #     # When: serial_port.is_open == True
    #     with patch.object(self.port, 'serial_port', Mock(is_open=True)):
    #         # Then: is_connected() == True
    #         self.assertTrue(self.port.is_connected())
