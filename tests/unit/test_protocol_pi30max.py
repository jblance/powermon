""" tests / pmon / unit / test_protocol_pi30max.py """
import unittest

from powermon.commands.command import Command
from powermon.device import DeviceInfo
# from powermon.libs.errors import InvalidCRC, InvalidResponse
from powermon.outputformats.simple import SimpleFormat
from powermon.protocols import get_protocol_definition
# proto = get_protocol_definition('PI30MAXA')  # uses pi30 with max model
proto = get_protocol_definition('PI30MAX')   # uses full pi30max class file


class TestProtocolPi30Max(unittest.TestCase):
    """ exercise different functions in PI30MAX protocol """

    def test_full_command_qvfw(self):
        """ test a for correct full command for QVFW """
        _result = proto.get_full_command(command="QVFW")
        expected = b'QVFWb\x99\r'
        # print(_result)
        self.assertEqual(_result, expected)

    def test_build_result_qvfw(self):
        """ test result build for QVFW """
        expected = ['main_cpu_firmware_version=00072.70']
        simple_formatter = SimpleFormat({"extra_info": True})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QVFW"})
        command.command_definition = proto.get_command_definition('QVFW')
        _result = command.build_result(raw_response=b"(VERFW:00072.70\x53\xA7\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qvfw_incorrect_crc(self):
        """ test result build for QVFW with an incorrect CRC"""
        expected = ['Error Count: 1',
            "Error #0: response has invalid CRC - got '\\x53\\xa6', calculated '\\x53\\xa7'"]
        simple_formatter = SimpleFormat({"extra_info": True})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QVFW"})
        command.command_definition = proto.get_command_definition('QVFW')
        _result = command.build_result(raw_response=b"(VERFW:00072.70\x53\xA6\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_get_id(self):
        """ test get id command - should return QID """
        expected = "QSID"
        res = proto.get_command_definition("get_id")
        # print(res.code)
        self.assertEqual(res.code, expected)

    def test_build_result_qpigs2(self):
        """ test result build for QPIGS2 """
        expected = ['pv2_input_current=3.1A', 'pv2_input_voltage=327.3V', 'pv2_charging_power=1026W']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QPIGS2"})
        command.command_definition = proto.get_command_definition('QPIGS2')
        _result = command.build_result(raw_response=b"(03.1 327.3 01026 \xc9\x8b\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qpiri(self):
        """ test result build for QPIRI """
        expected = ['ac_input_voltage=230.0V', 'ac_input_current=21.7A', 'ac_output_voltage=230.0V', 'ac_output_frequency=50.0Hz',
            'ac_output_current=21.7A', 'ac_output_apparent_power=5000VA', 'ac_output_active_power=4000W', 'battery_voltage=48.0V',
            'battery_recharge_voltage=46.0V', 'battery_under_voltage=42.0V', 'battery_bulk_charge_voltage=56.4V', 'battery_float_charge_voltage=54.0V',
            'battery_type=AGM', 'max_ac_charging_current=10A', 'max_charging_current=10A', 'input_voltage_range=UPS',
            'output_source_priority=Utility Solar Battery', 'charger_source_priority=Utility first', 'max_parallel_units=6', 'machine_type=Off Grid',
            'topology=transformerless', 'output_mode=single machine', 'battery_redischarge_voltage=54.0V',
            'pv_ok_condition=As long as one unit of inverters has connect PV, parallel system will consider PV OK',
            'pv_power_balance=PV input max power will be the sum of the max charged power and loads power']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QPIRI"})
        command.command_definition = proto.get_command_definition('QPIRI')
        _result = command.build_result(raw_response=b"(230.0 21.7 230.0 50.0 21.7 5000 4000 48.0 46.0 42.0 56.4 54.0 0 10 010 1 0 0 6 01 0 0 54.0 0 1\x6F\x7E\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_battery_options_qpiri(self):
        """ test battery options list of QPIRI """
        expected = ['AGM', 'Flooded', 'User', 'Pylontech', 'Shinheung', 'WECO', 'Soltaro', 'TBD', 'LIb-protocol compatible', '3rd party Lithium']
        command_definition = proto.get_command_definition('QPIRI')
        battery_options = command_definition.reading_definitions[12].options
        # print(battery_options)
        self.assertListEqual(expected, battery_options)

    def test_battery_options_2(self):
        """ test battery options 2 is 'User' """
        command_definition = proto.get_command_definition('QPIRI')
        cd = command_definition.get_reading_definition(lookup="Battery Type")
        result = cd.options[2]
        self.assertEqual(result, 'User')
