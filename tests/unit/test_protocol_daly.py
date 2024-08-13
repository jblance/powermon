""" tests / pmon / unit / test_protocol_daly.py """
import unittest

from powermon.commands.command import Command
from powermon.device import DeviceInfo
from powermon.libs.errors import InvalidCRC, InvalidResponse
from powermon.outputformats.simple import SimpleFormat
from powermon.protocols.daly import Daly as Proto
from powermon.ports.porttype import PortType

proto = Proto()


class TestProtocolDaly(unittest.TestCase):
    """ exercise different functions in DALY protocol """

    def test_check_crc(self):
        """ test a for correct CRC validation """
        # proto = Proto()
        result = proto.check_crc(response=b"\xa5\x01\x90\x08\x01\t\x00\x00u\xcf\x03\n\x99")
        self.assertTrue(result)

    def test_check_crc_incorrect(self):
        """ test an exception is raised if CRC validation fails """
        self.assertRaises(InvalidCRC, proto.check_crc, response=b"\xa5\x01\x90\x08\x01\t\x00\x00u\xcf\x03\n\x98")

    def test_check_valid_ok(self):
        """ test protocol returns true for a correct response validation check """
        _result = proto.check_valid(response=b"\xa5\x01\x90\x08\x01\t\x00\x00u\xcf\x03\n\x99")
        expected = True
        # print(_result)
        self.assertEqual(_result, expected)

    def test_check_valid_none(self):
        """ test protocol returns false for a None response validation check """
        self.assertRaises(InvalidResponse, proto.check_valid, response=None)

    def test_check_valid_short(self):
        """ test protocol returns false for a short response validation check """
        self.assertRaises(InvalidResponse, proto.check_valid, response=b"\xa5\x01\x90")

    def test_check_valid_missing(self):
        """ test protocol returns false for a response missing start char validation check """
        self.assertRaises(InvalidResponse, proto.check_valid, response=b"\xa4\x01\x90\x08\x01\t\x00\x00u\xcf\x03\n\x99")

    def test_construct_short_response(self):
        """ test for correct failure if response is too short for construct parsing """
        # proto = Proto()
        self.assertRaises(InvalidResponse, proto.split_response, response=b'', command_definition=proto.get_command_definition('SOC'))

    def test_full_command_soc_ble(self):
        """ test a for correct full command for SOC for a BLE device """
        # proto = Proto()
        proto.port_type = PortType.BLE
        _result = proto.get_full_command(command="SOC")
        expected = b'\xa5\x80\x90\x08\x00\x00\x00\x00\x00\x00\x00\x00\xbd'
        # print(_result)
        self.assertEqual(_result, expected)

    def test_full_command_soc_serial(self):
        """ test a for correct full command for SOC for a serial device """
        # proto = Proto()
        proto.port_type = PortType.SERIAL
        _result = proto.get_full_command(command="SOC")
        expected = b'\xa5\x40\x90\x08\x00\x00\x00\x00\x00\x00\x00\x00}\n'
        # print(_result)
        self.assertEqual(_result, expected)

    def test_trim(self):
        """ test protocol does a correct trim operation """
        _result = proto.trim_response(response=b"\xa5\x01\x90\x08\x01\t\x00\x00u\xcf\x03\n\x99", command_definition=proto.get_command_definition('SOC'))
        expected = b"\xa5\x01\x90\x08\x01\t\x00\x00u\xcf\x03\n\x99"
        # print(_result)
        self.assertEqual(_result, expected)

    def test_split(self):
        """ test protocol does a correct split operation """
        _result = proto.split_response(response=b"\xa5\x01\x90\x08\x01\t\x00\x00u\xcf\x03\n\x99", command_definition=proto.get_command_definition('SOC'))
        expected = [('start_flag', b'\xa5'), ('module_address', b'\x01'), ('command_id', b'\x90'), ('data_length', 8), ('battery_voltage', 265), ('acquistion_voltage', 0), ('current', 30159), ('soc', 778), ('checksum', b'\x99')]
        # print(_result)
        self.assertEqual(_result, expected)

    def test_build_result_soc(self):
        """ test result build for SOC """
        expected = ['battery_bank_voltage=26.5V', 'acquistion=0.0V', 'current=15.9A', 'soc=77.8%']
        simple_formatter = SimpleFormat({"extra_info": True})
        device_info = DeviceInfo(name="name", device_id="device_id", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "SOC"})
        command.command_definition = proto.get_command_definition('SOC')
        _result = command.build_result(raw_response=b"\xa5\x01\x90\x08\x01\t\x00\x00u\xcf\x03\n\x99", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)
