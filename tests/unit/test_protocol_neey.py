""" tests / pmon / unit / test_protocol_neey.py """
import unittest

from powermon.commands.command import Command
from powermon.device import DeviceInfo
from powermon.libs.errors import InvalidCRC, InvalidResponse
from powermon.outputformats.simple import SimpleFormat
# from powermon.ports import PortType
from powermon.protocols.neey import Neey as Proto

proto = Proto()

device_info_response = b'U\xaa\x11\x01\x01\x00d\x00GW-24S4EB\x00\x00\x00\x00\x00\x00\x00HW-2.8.0ZH-1.2.3V1.0.0\x00\x0020220916\x04\x00\x00\x00n\x85?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00G\xff'
cell_info_response = b'U\xaa\x11\x01\x02\x00,\x01\xed\xb2\x15S@4zT@\xe5}T@JuT@o{T@\xd0\x82T@ \x7fT@o{T@\xaflT@\x9aqT@\xf9xT@4zT@ \x7fT@_pT@[\x80T@\xb3\\T@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xee\x971>b9;>m\x852>\xb5\xf00>\x14R0>\xd1s3>\x86d5>\xdb\xaf7>f\xf7:>,\xa8@>\xb3)@>\x86\xcd=>\xf2W8>\xd3~3>\x19c1>^\xfe.>\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x9faTB\x9faT@\x00\x8f\xb6<\x05\x00\x0f\x05\xc4?\x81\xc0\xaeG\xf5A\xaeG\xf5A\x00\x00\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x8a\x8a\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xbe\xff'
multi_frame_response = b'U\xaa\x11\x01\x03\x00\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00(\xffU\xaa\x11\x01\x03\x00d\x00`\x1b\xbf?@(\xbf?\n\x9eK@33s@"p\xd5?0\xe7\xd4?\x7f\xf2\x00@\x00\x00\x00\x00\x00\x00\x80?33\xd3?\\\x8f\xd2?H\xe1\xba?\x00\x00\xaaB\x00\x00\x82B\x04\x00\x00\x00~\x11E\x0020220916\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x97\xff'

class TestProtocolNeey(unittest.TestCase):
    """ exercise different functions in NEEY protocol """

    def test_check_crc(self):
        """ test a for correct CRC validation """
        # proto = Proto()
        result = proto.check_crc(response=device_info_response)
        self.assertTrue(result)

    def test_check_crc_incorrect(self):
        """ test an exception is raised if CRC validation fails """
        self.assertRaises(InvalidCRC, proto.check_crc, response=device_info_response[:-2])

    def test_check_crc_extra_frames(self):
        """ test crc correct for multiple frames in response """
        result = proto.check_crc(response=multi_frame_response)
        self.assertTrue(result)

    def test_check_valid_ok(self):
        """ test protocol returns true for a correct response validation check """
        _result = proto.check_valid(response=device_info_response)
        expected = True
        # print(_result)
        self.assertEqual(_result, expected)

    def test_check_valid_none(self):
        """ test protocol returns false for a None response validation check """
        self.assertRaises(InvalidResponse, proto.check_valid, response=None)

    def test_check_valid_short(self):
        """ test protocol returns false for a short response validation check """
        self.assertRaises(InvalidResponse, proto.check_valid, response=device_info_response[:-2])

    def test_check_valid_missing(self):
        """ test protocol returns false for a response missing start char validation check """
        self.assertRaises(InvalidResponse, proto.check_valid, response=device_info_response[1:])

    def test_construct_short_response(self):
        """ test for correct failure if response is too short for construct parsing """
        # proto = Proto()
        self.assertRaises(InvalidResponse, proto.split_response, response=b'', command_definition=proto.get_command_definition('device_info'))

    def test_full_command_device_info(self):
        """ test a for correct full command for device_info """
        _result = proto.get_full_command(command="device_info")
        expected = b'\xaaU\x11\x01\x01\x00\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfa\xff'
        # print(_result)
        self.assertEqual(_result, expected)

    def test_full_command_cell_info(self):
        """ test a for correct full command for cell_info """
        _result = proto.get_full_command(command="cell_info")
        expected = b'\xaaU\x11\x01\x02\x00\x00\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf9\xff'
        # print(_result)
        self.assertEqual(_result, expected)

    def test_full_command_factory_defaults(self):
        """ test a for correct full command for factory_defaults """
        _result = proto.get_full_command(command="factory_defaults")
        expected = b'\xaaU\x11\x01\x03\x00\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf8\xff'
        # print(_result)
        self.assertEqual(_result, expected)

    def test_full_command_get_settings(self):
        """ test a for correct full command for get_settings """
        _result = proto.get_full_command(command="get_settings")
        expected = b'\xaaU\x11\x01\x04\x00\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff'
        # print(_result)
        self.assertEqual(_result, expected)


    def test_full_command_balancer_on(self):
        """ test a for correct full command for balancer on """
        _result = proto.get_full_command(command="balancer_on")
        expected = b'\xaaU\x11\x00\x05\x0D\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\xF3\xFF'
        # print()
        # print(expected)
        # print(_result)
        self.assertEqual(_result, expected)

    def test_full_command_balancer_off(self):
        """ test a for correct full command for balancer off """
        _result = proto.get_full_command(command="balancer_off")
        expected = b'\xaaU\x11\x00\x05\x0D\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xF2\xFF'
        # print()
        # print(expected)
        # print(_result)
        self.assertEqual(_result, expected)

    def test_full_command_cell_count_one(self):
        """ test a for correct full command for cell count 1 """
        _result = proto.get_full_command(command="cell_count=1")
        expected = bytes.fromhex('aa551100 0501 1400 01000000000000000000 ffff')
        # print()
        # print(expected)
        # print(_result)
        self.assertEqual(_result, expected)

    def test_full_command_cell_count_24(self):
        """ test a for correct full command for cell count 24 """
        _result = proto.get_full_command(command="cell_count=24")
        expected = bytes.fromhex('aa551100 0501 1400 18000000000000000000 e6ff')
        # print()
        # print(expected)
        # print(_result)
        self.assertEqual(_result, expected)

    def test_full_command_balance_current_1_0(self):
        """ test a for correct full command for balance_current=1.0 """
        _result = proto.get_full_command(command="balance_current=1.0")
        expected = bytes.fromhex('aa551100 0503 1400 0000803f000000000000 43ff')
        # print()
        # print(expected)
        # print(_result)
        self.assertEqual(_result, expected)

    def test_full_command_balance_current_1(self):
        """ test a for correct full command for balance_current=1 """
        _result = proto.get_full_command(command="balance_current=1")
        expected = bytes.fromhex('aa551100 0503 1400 0000803f000000000000 43ff')
        # print()
        # print(expected)
        # print(_result)
        self.assertEqual(_result, expected)

    def test_full_command_mbc_1_0(self):
        """ test a for correct full command for mbc=1.0 """
        _result = proto.get_full_command(command="mbc=1.0")
        expected = bytes.fromhex('aa551100 0503 1400 0000803f000000000000 43ff')
        # print()
        # print(expected)
        # print(_result)
        self.assertEqual(_result, expected)

    def test_full_command_max_balance_current_1_0(self):
        """ test a for correct full command for max_balance_current=1.0 """
        _result = proto.get_full_command(command="max_balance_current=1.0")
        expected = bytes.fromhex('aa551100 0503 1400 0000803f000000000000 43ff')
        # print()
        # print(expected)
        # print(_result)
        self.assertEqual(_result, expected)

    def test_full_command_balance_current_4_0(self):
        """ test a for correct full command for balance_current=4.0 """
        _result = proto.get_full_command(command="balance_current=4.0")
        expected = b'\xaaU\x11\x00\x05\x03\x14\x00\x00\x00\x80@\x00\x00\x00\x00\x00\x00<\xff'
        # print()
        # print(expected)
        # print(_result)
        self.assertEqual(_result, expected)

    def test_trim(self):
        """ test protocol does a correct trim operation """
        _result = proto.trim_response(response=device_info_response, command_definition=proto.get_command_definition('device_info'))
        expected = b'U\xaa\x11\x01\x01\x00d\x00GW-24S4EB\x00\x00\x00\x00\x00\x00\x00HW-2.8.0ZH-1.2.3V1.0.0\x00\x0020220916\x04\x00\x00\x00n\x85?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00G\xff'
        # print(_result)
        self.assertEqual(_result, expected)

    def test_split(self):
        """ test protocol does a correct split operation """
        _result = proto.split_response(response=device_info_response, command_definition=proto.get_command_definition('device_info'))
        expected = [('start_flag', b'U\xaa'), ('module_address', b'\x11'), ('function', b'\x01'), ('command', 1), ('length', 100), ('model', b'GW-24S4EB\x00\x00\x00\x00\x00\x00\x00'), ('hw_version', b'HW-2.8.0'), ('sw_version', b'ZH-1.2.3'), ('protocol_version', b'V1.0.0\x00\x00'), ('production_date', b'20220916'), ('power_on_count', 4), ('total_runtime', 4162926), ('unused', b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'), ('crc', b'G'), ('end_flag', b'\xff')]
        # print(_result)
        self.assertEqual(_result, expected)

    def test_build_result_device_info(self):
        """ test result build for device_info """
        expected = ['model=GW-24S4EB', 'hw_version=HW-2.8.0', 'sw_version=ZH-1.2.3', 'protocol_version=V1.0.0', 'production_date=20220916', 'power_on_count=4', 'total_runtime=4162926sec']
        simple_formatter = SimpleFormat({})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "device_info"})
        command.command_definition = proto.get_command_definition('device_info')
        _result = command.build_result(raw_response=device_info_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_cell_info(self):
        """ test result build for cell_info """
        expected = ['cell_01_voltage=3.2982V', 'cell_02_voltage=3.32V', 'cell_03_voltage=3.3202V', 'cell_04_voltage=3.3197V', 'cell_05_voltage=3.32V', 'cell_06_voltage=3.3205V', 'cell_07_voltage=3.3203V', 'cell_08_voltage=3.32V', 'cell_09_voltage=3.3191V', 'cell_10_voltage=3.3194V', 'cell_11_voltage=3.3199V', 'cell_12_voltage=3.32V', 'cell_13_voltage=3.3203V', 'cell_14_voltage=3.3194V', 'cell_15_voltage=3.3203V', 'cell_16_voltage=3.3182V', 'cell_01_resistance=0.17343Ω', 'cell_02_resistance=0.18284Ω', 'cell_03_resistance=0.17434Ω', 'cell_04_resistance=0.17279Ω', 'cell_05_resistance=0.17219Ω', 'cell_06_resistance=0.17525Ω', 'cell_07_resistance=0.17714Ω', 'cell_08_resistance=0.17938Ω', 'cell_09_resistance=0.18258Ω', 'cell_10_resistance=0.18814Ω', 'cell_11_resistance=0.18766Ω', 'cell_12_resistance=0.18535Ω', 'cell_13_resistance=0.18002Ω', 'cell_14_resistance=0.17529Ω', 'cell_15_resistance=0.17323Ω', 'cell_16_resistance=0.17089Ω', 'total_voltage=53.0953V', 'average_cell_voltage=3.3185V', 'delta_cell_voltage=0.0223V', 'max_voltage_cell=6', 'min_voltage_cell=1', 'operation_status=Balancing', 'balancing_current=-4.039A', 'temperature_1=30.65999984741211°C', 'temperature_2=30.65999984741211°C', 'cell_detection_failed=0x00 0x00 0xff', 'cell_overvoltage_failed=0x00 0x00 0x00', 'cell_undervoltage_failed=0x00 0x00 0x00', 'cell_polarity_error=0x00 0x00 0x00', 'excessive_line_resistance=0x00 0x00 0x00', 'overheating=0x0', 'charging_fault=0x0', 'discharge_fault=0x0', 'read_write_error=0x0']
        simple_formatter = SimpleFormat({})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "cell_info"})
        command.command_definition = proto.get_command_definition('cell_info')
        _result = command.build_result(raw_response=cell_info_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)
