""" tests / pmon / unit / test_protocol_pi18.py """
import unittest
from powermon.commands.command import Command
from powermon.device import DeviceInfo
from powermon.libs.errors import InvalidCRC, InvalidResponse, CommandDefinitionMissing
from powermon.outputformats.simple import SimpleFormat
from powermon.protocols import get_protocol_definition
proto = get_protocol_definition('PI18')


class TestProtocolPI18(unittest.TestCase):
    """ exercise different functions in jkserial protocol """

    def test_check_crc_good(self):
        """ test a for correct CRC validation """
        response = b"^D0882300,217,2300,500,217,5000,5000,480,480,530,440,570,570,2,10,070,1,1,1,9,0,0,0,0,1,00\xe1k\r"
        result = proto.check_crc(response=response, command_definition=proto.get_command_definition('PIRI'))
        self.assertTrue(result)

    def test_check_crc_incorrect(self):
        """ test a for failing CRC validation (crc is wrong) """
        response = b"^D0882300,217,2300,500,217,5000,5000,480,480,530,440,570,570,2,10,070,1,1,1,9,0,0,0,0,1,00\xe2k\r"
        #result = proto.check_crc(response=response, command_definition=proto.get_command_definition('PIRI'))
        self.assertRaises(InvalidCRC, proto.check_crc, response=response, command_definition=proto.get_command_definition('PIRI'))

    def test_check_crc_wrong_response_start(self):
        """ test a for failing CRC validation (not a response that starts with ^D) """
        response = b"0882300,217,2300,500,217,5000,5000,480,480,530,440,570,570,2,10,070,1,1,1,9,0,0,0,0,1,00\xe1k\r"
        # result = proto.check_crc(response=response, command_definition=proto.get_command_definition('PIRI'))
        self.assertRaises(InvalidResponse, proto.check_crc, response=response, command_definition=proto.get_command_definition('PIRI'))
        # self.assertFalse(result)

    def test_get_full_command_piri(self):
        """ test full command generation for PIRI command """
        fc = proto.get_full_command('PIRI')
        # print(fc)
        expected = b'^P007PIRI\xee8\r'
        self.assertEqual(expected, fc)

    def test_get_full_command_pi(self):
        """ test full command generation for PI command """
        fc = proto.get_full_command('PI')
        # print(fc)
        expected = b'^P005PIq\x8b\r'
        self.assertEqual(expected, fc)

    def test_build_result_pop0(self):
        """ test result build for POP0 - success """
        expected = ['set_device_output_source_priority=Succeeded']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "POP0"})
        command.command_definition = proto.get_command_definition('POP0')
        _result = command.build_result(raw_response=b"^1\x0b\xc2\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_pop1(self):
        """ test result build for POP1 - fail """
        expected = ['set_device_output_source_priority=Failed']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "POP1"})
        command.command_definition = proto.get_command_definition('POP1')
        _result = command.build_result(raw_response=b"^0\x1b\xe3\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_pop2(self):
        """ test result build for POP2 - invalid command """
        # expected = ['set_device_output_source_priority=Failed']
        # simple_formatter = SimpleFormat({"extra_info": False})
        # device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        # command = Command.from_config({"command": "POP2"})
        self.assertRaises(CommandDefinitionMissing, proto.get_command_definition, 'POP2')

    def test_build_result_mchgc(self):
        """ test result build for MCHGV - success """
        expected = ['set_battery_bulk,float_charging_voltages=Succeeded']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "MCHGV552,540"})
        command.command_definition = proto.get_command_definition('MCHGV552,540')
        _result = command.build_result(raw_response=b"^1\x0b\xc2\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_check_crc_flag(self):
        """ test a for correct CRC validation """
        response = b"^D0200,0,0,0,0,1,0,0,12\xc2\x39\r"
        result = proto.check_crc(response=response, command_definition=proto.get_command_definition('FLAG'))
        self.assertTrue(result)

    def test_build_result_flag(self):
        """ test result build for flag - success """
        expected = ['buzzer_beep=disabled', 'overload_bypass_function=disabled', 'display_back_to_default_page=disabled', 'overload_restart=disabled', 'over_temperature_restart=disabled', 'backlight_on=enabled', 'alarm_primary_source_interrupt=disabled', 'fault_code_record=disabled', 'reserved=12']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "FLAG"})
        command.command_definition = proto.get_command_definition('FLAG')
        _result = command.build_result(raw_response=b"^D0200,0,0,0,0,1,0,0,12\xc2\x39\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_vfw(self):
        """ test result build for vfw """
        expected = ['main_cpu_version=5220', 'slave_1_cpu_version=0', 'slave_2_cpu_version=0']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "VFW"})
        command.command_definition = proto.get_command_definition('VFW')
        _result = command.build_result(raw_response=b"^D02005220,00000,00000\x3e\xf8\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)
