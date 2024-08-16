""" tests / pmon / unit / test_protocol_neey.py """
import unittest

from powermon.commands.command import Command
from powermon.device import DeviceInfo
from powermon.libs.errors import InvalidCRC, InvalidResponse
from powermon.outputformats.simple import SimpleFormat
from powermon.protocols.neey import Neey as Proto
from powermon.ports.porttype import PortType

proto = Proto()

device_info_response = b'U\xaa\x11\x01\x01\x00d\x00GW-24S4EB\x00\x00\x00\x00\x00\x00\x00HW-2.8.0ZH-1.2.3V1.0.0\x00\x0020220916\x04\x00\x00\x00n\x85?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00G\xff'
cell_info_response = b'U\xaa\x11\x01\x02\x00,\x01\xed\xb2\x15S@4zT@\xe5}T@JuT@o{T@\xd0\x82T@ \x7fT@o{T@\xaflT@\x9aqT@\xf9xT@4zT@ \x7fT@_pT@[\x80T@\xb3\\T@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xee\x971>b9;>m\x852>\xb5\xf00>\x14R0>\xd1s3>\x86d5>\xdb\xaf7>f\xf7:>,\xa8@>\xb3)@>\x86\xcd=>\xf2W8>\xd3~3>\x19c1>^\xfe.>\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x9faTB\x9faT@\x00\x8f\xb6<\x05\x00\x0f\x05\xc4?\x81\xc0\xaeG\xf5A\xaeG\xf5A\x00\x00\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x8a\x8a\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xbe\xff'

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
        expected = ['start_flag=0X55 0XAA', 'module_address=0x11', 'function=0x1', 'command=1', 'length=100', 'model=GW-24S4EB', 'hw_version=HW-2.8.0', 'sw_version=ZH-1.2.3', 'protocol_version=V1.0.0', 'production_date=20220916', 'power_on_count=4', 'total_runtime=4162926sec', 'crc=0x47', 'end_flag=0xff']
        simple_formatter = SimpleFormat({})
        device_info = DeviceInfo(name="name", device_id="device_id", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "device_info"})
        command.command_definition = proto.get_command_definition('device_info')
        _result = command.build_result(raw_response=device_info_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    # def test_build_result_cell_info(self):
    #     """ test result build for cell_info """
    #     expected = []
    #     simple_formatter = SimpleFormat({})
    #     device_info = DeviceInfo(name="name", device_id="device_id", model="model", manufacturer="manufacturer")
    #     command = Command.from_config({"command": "cell_info"})
    #     command.command_definition = proto.get_command_definition('cell_info')
    #     _result = command.build_result(raw_response=cell_info_response, protocol=proto)
    #     formatted_data = simple_formatter.format(command, _result, device_info)
    #     print(formatted_data)
    #     self.assertEqual(formatted_data, expected)
