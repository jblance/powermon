""" tests / pmon / unit / test_format_json.py """
import unittest

from powermon.commands.command import Command
# from powermon.commands.command_definition import CommandDefinition
# from powermon.commands.reading import Reading
# from powermon.commands.reading_definition import (ReadingDefinition,
                                                #   ReadingType, ResponseType)
# from powermon.commands.result import Result, ResultType
from powermon.device import DeviceInfo
from powermon.libs.errors import ConfigError
from powermon.outputformats.bmsresponse import BMSResponse as fmt
from powermon.protocols.jkserial import JkSerial as Proto

proto = Proto()


class TestFormatBMSResponse(unittest.TestCase):
    """ test the BMSResponse formatter """
    def test_bmsresponse_format_pi30_all(self):
        """ - test pi30 bmsresponse format (jkserial response) - with all config items """
        expected = ['BMS0 098 0 0 0 544 520 104 0600 1200']
        formatter = fmt({'protocol': 'pi30', 'force_charge': False, 'battery_charge_voltage': 54.4, 'battery_float_voltage': 52, 'battery_cutoff_voltage': 48, 'battery_max_charge_current': 100, 'battery_max_discharge_current': 100})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "all_data"})
        command.command_definition = proto.get_command_definition('all_data')
        raw_response=bytes.fromhex("4e 57 00 fd 00 00 00 00 06 00 01 79 0c 01 0d 06 02 0d 06 03 0d 07 04 0d 07 80 00 10 81 00 0e 82 00 0d 83 05 35 84 00 00 85 62 86 02 87 00 00 89 00 00 00 05 8a 00 04 8b 00 03 8c 00 03 8e 05 a0 8f 04 10 90 0e 10 91 0d de 92 00 05 93 0a 28 94 0a 5a 95 00 05 96 01 2c 97 00 78 98 00 1e 99 00 3c 9a 00 1e 9b 0d 48 9c 00 05 9d 01 9e 00 50 9f 00 41 a0 00 64 a1 00 64 a2 00 14 a3 00 32 a4 00 37 a5 00 03 a6 00 08 a7 ff ec a8 ff f6 a9 04 aa 00 00 01 31 ab 01 ac 01 ad 03 7e ae 01 af 00 b0 00 0a b1 14 b2 35 33 31 34 00 00 00 00 00 00 b3 00 b4 49 6e 70 75 74 20 55 73 b5 32 33 31 32 b6 00 00 36 a6 b7 31 31 2e 58 57 5f 53 31 31 2e 32 31 48 5f 5f b8 00 b9 00 00 01 31 ba 49 6e 70 75 74 20 55 73 65 72 64 61 45 64 64 69 65 42 6c 75 65 42 4d 53 c0 01 00 00 00 00 68 00 00 44 6f")

        _result = command.build_result(raw_response=raw_response, protocol=proto)
        formatted_data = formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_bmsresponse_format_invalid_protocol(self):
        """ - test bmsresponse format - with invalid protocol """
        formatter = fmt({'protocol': 'invalid', 'force_charge': False, 'battery_charge_voltage': 54.4, 'battery_float_voltage': 52, 'battery_cutoff_voltage': 48, 'battery_max_charge_current': 100, 'battery_max_discharge_current': 100})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "all_data"})
        command.command_definition = proto.get_command_definition('all_data')
        raw_response=bytes.fromhex("4e 57 00 fd 00 00 00 00 06 00 01 79 0c 01 0d 06 02 0d 06 03 0d 07 04 0d 07 80 00 10 81 00 0e 82 00 0d 83 05 35 84 00 00 85 62 86 02 87 00 00 89 00 00 00 05 8a 00 04 8b 00 03 8c 00 03 8e 05 a0 8f 04 10 90 0e 10 91 0d de 92 00 05 93 0a 28 94 0a 5a 95 00 05 96 01 2c 97 00 78 98 00 1e 99 00 3c 9a 00 1e 9b 0d 48 9c 00 05 9d 01 9e 00 50 9f 00 41 a0 00 64 a1 00 64 a2 00 14 a3 00 32 a4 00 37 a5 00 03 a6 00 08 a7 ff ec a8 ff f6 a9 04 aa 00 00 01 31 ab 01 ac 01 ad 03 7e ae 01 af 00 b0 00 0a b1 14 b2 35 33 31 34 00 00 00 00 00 00 b3 00 b4 49 6e 70 75 74 20 55 73 b5 32 33 31 32 b6 00 00 36 a6 b7 31 31 2e 58 57 5f 53 31 31 2e 32 31 48 5f 5f b8 00 b9 00 00 01 31 ba 49 6e 70 75 74 20 55 73 65 72 64 61 45 64 64 69 65 42 6c 75 65 42 4d 53 c0 01 00 00 00 00 68 00 00 44 6f")

        _result = command.build_result(raw_response=raw_response, protocol=proto)
        self.assertRaises(ConfigError, formatter.format, command, _result, device_info)

    def test_bmsresponse_format_pi30_missing_config_all(self):
        """ - test pi30 bmsresponse format (jkserial response) - with missing config items """
        formatter = fmt({'protocol': 'pi30'})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "all_data"})
        command.command_definition = proto.get_command_definition('all_data')
        raw_response=bytes.fromhex("4e 57 00 fd 00 00 00 00 06 00 01 79 0c 01 0d 06 02 0d 06 03 0d 07 04 0d 07 80 00 10 81 00 0e 82 00 0d 83 05 35 84 00 00 85 62 86 02 87 00 00 89 00 00 00 05 8a 00 04 8b 00 03 8c 00 03 8e 05 a0 8f 04 10 90 0e 10 91 0d de 92 00 05 93 0a 28 94 0a 5a 95 00 05 96 01 2c 97 00 78 98 00 1e 99 00 3c 9a 00 1e 9b 0d 48 9c 00 05 9d 01 9e 00 50 9f 00 41 a0 00 64 a1 00 64 a2 00 14 a3 00 32 a4 00 37 a5 00 03 a6 00 08 a7 ff ec a8 ff f6 a9 04 aa 00 00 01 31 ab 01 ac 01 ad 03 7e ae 01 af 00 b0 00 0a b1 14 b2 35 33 31 34 00 00 00 00 00 00 b3 00 b4 49 6e 70 75 74 20 55 73 b5 32 33 31 32 b6 00 00 36 a6 b7 31 31 2e 58 57 5f 53 31 31 2e 32 31 48 5f 5f b8 00 b9 00 00 01 31 ba 49 6e 70 75 74 20 55 73 65 72 64 61 45 64 64 69 65 42 6c 75 65 42 4d 53 c0 01 00 00 00 00 68 00 00 44 6f")

        _result = command.build_result(raw_response=raw_response, protocol=proto)
        self.assertRaises(ConfigError, formatter.format, command, _result, device_info)

    def test_bmsresponse_format_pi30_missing_config_float(self):
        """ - test pi30 bmsresponse format (jkserial response) - with missing battery_float_voltage config item """
        formatter = fmt({'protocol': 'pi30', 'force_charge': False, 'battery_charge_voltage': 54.4, 'battery_cutoff_voltage': 48, 'battery_max_charge_current': 100, 'battery_max_discharge_current': 100})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "all_data"})
        command.command_definition = proto.get_command_definition('all_data')
        raw_response=bytes.fromhex("4e 57 00 fd 00 00 00 00 06 00 01 79 0c 01 0d 06 02 0d 06 03 0d 07 04 0d 07 80 00 10 81 00 0e 82 00 0d 83 05 35 84 00 00 85 62 86 02 87 00 00 89 00 00 00 05 8a 00 04 8b 00 03 8c 00 03 8e 05 a0 8f 04 10 90 0e 10 91 0d de 92 00 05 93 0a 28 94 0a 5a 95 00 05 96 01 2c 97 00 78 98 00 1e 99 00 3c 9a 00 1e 9b 0d 48 9c 00 05 9d 01 9e 00 50 9f 00 41 a0 00 64 a1 00 64 a2 00 14 a3 00 32 a4 00 37 a5 00 03 a6 00 08 a7 ff ec a8 ff f6 a9 04 aa 00 00 01 31 ab 01 ac 01 ad 03 7e ae 01 af 00 b0 00 0a b1 14 b2 35 33 31 34 00 00 00 00 00 00 b3 00 b4 49 6e 70 75 74 20 55 73 b5 32 33 31 32 b6 00 00 36 a6 b7 31 31 2e 58 57 5f 53 31 31 2e 32 31 48 5f 5f b8 00 b9 00 00 01 31 ba 49 6e 70 75 74 20 55 73 65 72 64 61 45 64 64 69 65 42 6c 75 65 42 4d 53 c0 01 00 00 00 00 68 00 00 44 6f")

        _result = command.build_result(raw_response=raw_response, protocol=proto)
        self.assertRaises(ConfigError, formatter.format, command, _result, device_info)
