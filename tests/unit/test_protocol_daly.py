""" tests / pmon / unit / test_protocol_daly.py """
import unittest

from powermon.commands.command import Command
from powermon.device import DeviceInfo
from powermon.libs.errors import InvalidCRC, InvalidResponse
from powermon.outputformats.simple import SimpleFormat
from powermon.ports import PortType
from powermon.protocols import get_protocol_definition
proto = get_protocol_definition('DALY')


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
        expected = ['battery_bank_voltage=26.5V', 'current=15.9A', 'soc=77.8%']
        simple_formatter = SimpleFormat({"extra_info": True})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "SOC"})
        command.command_definition = proto.get_command_definition('SOC')
        _result = command.build_result(raw_response=b"\xa5\x01\x90\x08\x01\t\x00\x00u\xcf\x03\n\x99", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)


    def test_build_result_cell_voltages(self):
        """ test result build for cell voltages """
        expected = ['cell_01_voltage=3.413V', 'cell_02_voltage=3.396V', 'cell_03_voltage=3.406V', 'cell_04_voltage=3.425V', 'cell_05_voltage=3.42V', 'cell_06_voltage=3.404V', 'cell_07_voltage=3.402V', 'cell_08_voltage=3.414V', 'cell_09_voltage=3.412V', 'cell_10_voltage=3.417V', 'cell_11_voltage=3.422V', 'cell_12_voltage=3.426V', 'cell_13_voltage=3.41V', 'cell_14_voltage=3.422V', 'cell_15_voltage=3.416V', 'cell_16_voltage=3.403V']
        raw_response = b'\xa5\x01\x95\x08\x01\rU\rD\rN\x89\xdb\xa5\x01\x95\x08\x02\ra\r\\\rL\x89\xfe\xa5\x01\x95\x08\x03\rJ\rV\rT\x89\xea\xa5\x01\x95\x08\x04\rY\r^\rb\x89\x10\xa5\x01\x95\x08\x05\rR\r^\rX\x89\x00\xa5\x01\x95\x08\x06\rK\x00\x00\x00\x00\x89*\xa5\x01\x95\x08\x07\x00\x00\x00\x00\x00\x00\x89\xd3\xa5\x01\x95\x08\x08\x00\x00\x00\x00\x00\xa5\x01\x95\x08\t\x00\x00\x00\x00\x00\x00\x89\xd5\xa5\x01\x95\x08\n\x00\x00\x00\x00\x00\x00\x89\xd6\xa5\x01\x95\x08\x0b\x00\x00\x00\x00\x00\x00\x89\xd7\xa5\x01\x95\x08\xa8\x00@\x00\x00 @\x00\r0\x00\x00\x00 @\x00\xf3Z\x00\x00m2\x00\x00\x00 @\x00S1\x00\x00\x00\x00\x00\xa5\x01\x95\x08\x0f\x00\x00\x00\x00\x00\x00\x89\xdb\xa5\x01\x95\x08\x10\x00\x00\x00\x00\x00\x00\x89\xdc'
        simple_formatter = SimpleFormat({"extra_info": True})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "cell_voltages"})
        command.command_definition = proto.get_command_definition('cell_voltages')
        _result = command.build_result(raw_response=raw_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_cell_voltages_broken(self):
        """ test result build for cell voltages with broken data """
        expected = ['cell_10_voltage=3.283V', 'cell_11_voltage=3.284V', 'cell_12_voltage=3.283V', 'cell_13_voltage=3.284V', 'cell_14_voltage=3.283V', 'cell_15_voltage=3.284V', 'cell_16_voltage=3.282V', 'cell_17_voltage=3.283V', 'cell_18_voltage=3.284V', 'cell_01_voltage=3.285V', 'cell_02_voltage=3.284V', 'cell_03_voltage=3.283V', 'cell_04_voltage=3.284V', 'cell_05_voltage=3.283V', 'cell_06_voltage=3.284V', 'cell_07_voltage=3.283V', 'cell_08_voltage=3.284V', 'cell_09_voltage=3.283V', 'cell_10_voltage=3.284V', 'cell_11_voltage=3.283V', 'cell_12_voltage=3.284V', 'cell_13_voltage=3.283V', 'cell_14_voltage=3.284V', 'cell_15_voltage=3.283V', 'cell_16_voltage=3.282V', 'cell_17_voltage=3.284V', 'cell_18_voltage=3.283V']
        raw_response = b'\xd4\x0c\xd3\x0c\xd4\x82g\xa5\x01\x95\x08\x04\x0c\xd3\x0c\xd4\x0c\xd3\x82g\xa5\x01\x95\x08\x05\x0c\xd4\x0c\xd3\x0c\xd4\x82i\xa5\x01\x95\x08\x06\x0c\xd2\x0c\xd3\x0c\xd4\x82h\xa5\x01\x95\x08\x01\x0c\xd5\x0c\xd4\x0c\xd3\x82f\xa5\x01\x95\x08\x02\x0c\xd4\x0c\xd3\x0c\xd4\x82f\xa5\x01\x95\x08\x03\x0c\xd3\x0c\xd4\x0c\xd3\x82f\xa5\x01\x95\x08\x04\x0c\xd4\x0c\xd3\x0c\xd4\x82h\xa5\x01\x95\x08\x05\x0c\xd3\x0c\xd4\x0c\xd3\x82h\xa5\x01\x95\x08\x06\x0c\xd2\x0c\xd4\x0c\xd3\x82h\xa5\x01\x93\x08\x02\x01\x01\x1f\x00\x01\xa60;\xa5\x01\x96\x08\x017\x00\x00\x00\x00\x000\xac\xa5\x01\x94\x08\x10\x01\x00\x00\x00\x00\x0fT\xb6'
        simple_formatter = SimpleFormat({"extra_info": True})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "cell_voltages"})
        command.command_definition = proto.get_command_definition('cell_voltages')
        _result = command.build_result(raw_response=raw_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)
