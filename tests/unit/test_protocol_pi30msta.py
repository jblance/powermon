""" tests / pmon / unit / test_protocol_pi30.py """
import unittest

from powermon.commands.command import Command
from powermon.device import DeviceInfo
from powermon.libs.errors import InvalidCRC, InvalidResponse
from powermon.outputformats.simple import SimpleFormat
from powermon.protocols import get_protocol_definition

# import construct as cs
proto = get_protocol_definition('PI30MSTA')
#proto = Proto()


class TestProtocolPi30MstA(unittest.TestCase):
    """ exercise different functions in PI30MSTA protocol """

    def test_full_command_qpigs2(self):
        """ test a for correct full command for QPIGS2 """
        _result = proto.get_full_command(command="QPIGS2")
        expected = b'QPIGS2h-\r'
        # print(_result)
        self.assertEqual(_result, expected)

    def test_build_result_qpigs2(self):
        """ test result build for QPIGS2 """
        expected = ['pv2_input_current=3.1A current mdi:solar-power measurement', 'pv2_input_voltage=327.3V voltage mdi:solar-power measurement', 'battery_voltage_from_scc_2=52.3V voltage mdi:solar-power measurement', 'pv2_charging_power=123W power mdi:solar-power measurement', 'device_status=1', 'ac_charging_current=1234.0A current mdi:transmission-tower-export measurement', 'ac_charging_power=122W power mdi:transmission-tower-export measurement', 'pv3_input_current=327.1A current mdi:solar-power measurement', 'pv3_input_voltage=52.4V voltage mdi:solar-power measurement', 'battery_voltage_from_scc_3=234.0V voltage mdi:solar-power measurement', 'pv3_charging_power=567W power mdi:solar-power measurement']
        simple_formatter = SimpleFormat({"extra_info": True})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QPIGS2"})
        command.command_definition = proto.get_command_definition('QPIGS2')
        test_response = command.command_definition.test_responses[0]
        _result = command.build_result(raw_response=test_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)


    def test_get_id(self):
        """ test get id command - should return QSID """
        expected = "QSID"
        res = proto.get_command_definition("get_id")
        # print(res.code)
        self.assertEqual(res.code, expected)
