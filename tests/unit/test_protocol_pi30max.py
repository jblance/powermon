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

    def test_build_result_qid(self):
        """ test result build for QID """
        expected = ['serial_number=9293333010501']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QID"})
        command.command_definition = proto.get_command_definition('QID')
        test_response = command.command_definition.test_responses[0]
        _result = command.build_result(raw_response=test_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qsid(self):
        """ test result build for QSID """
        expected = ['serial_number=92932105105335']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QSID"})
        command.command_definition = proto.get_command_definition('QSID')
        test_response = command.command_definition.test_responses[0]
        _result = command.build_result(raw_response=test_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

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


    def test_build_result_qled(self):
        """ test result build for QLED """
        expected = ['led_enabled=Enabled', 'led_speed=Medium', 'led_effect=Solid', 'led_brightness=5', 'led_number_of_colors=3', 'rgb=148000211255255255000255255']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QLED"})
        command.command_definition = proto.get_command_definition('QLED')
        _result = command.build_result(raw_response=b"(1 1 2 5 3 148000211255255255000255255\xdaj\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qey(self):
        """ test result build for QEY """
        expected = ['pv_generated_energy_for_year=238800Wh', 'year=2025']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QEY2025"})
        command.command_definition = proto.get_command_definition('QEY2025')
        _result = command.build_result(raw_response=b"(00238800!J\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qem(self):
        """ test result build for QEM """
        expected = ['pv_generated_energy_for_month=238800Wh', 'year=2025', 'month=March']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QEM202503"})
        command.command_definition = proto.get_command_definition('QEM202503')
        _result = command.build_result(raw_response=b"(00238800!J\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qed(self):
        """ test result build for QED """
        expected = ['pv_generated_energy_for_day=238800Wh', 'year=2025', 'month=March', 'day=2']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QED20250302"})
        command.command_definition = proto.get_command_definition('QED20250302')
        _result = command.build_result(raw_response=b"(00238800!J\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qet(self):
        """ test result build for QET """
        expected = ['total_pv_generated_energy=238800Wh']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QET"})
        command.command_definition = proto.get_command_definition('QET')
        _result = command.build_result(raw_response=b"(00238800!J\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qly(self):
        """ test result build for QLY """
        expected = ['output_load_energy_for_year=238800Wh', 'year=2025']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QLY2025"})
        command.command_definition = proto.get_command_definition('QLY2025')
        _result = command.build_result(raw_response=b"(00238800!J\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qlm(self):
        """ test result build for QLM """
        expected = ['output_load_energy_for_month=238800Wh', 'year=2025', 'month=March']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QLM202503"})
        command.command_definition = proto.get_command_definition('QLM202503')
        _result = command.build_result(raw_response=b"(00238800!J\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qld(self):
        """ test result build for QLD """
        expected = ['output_load_energy_for_day=238800Wh', 'year=2025', 'month=March', 'day=2']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QLD20250302"})
        command.command_definition = proto.get_command_definition('QLD20250302')
        _result = command.build_result(raw_response=b"(00238800!J\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qlt(self):
        """ test result build for QLT """
        expected = ['total_output_load_energy=238800Wh']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QLT"})
        command.command_definition = proto.get_command_definition('QLT')
        _result = command.build_result(raw_response=b"(00238800!J\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qbeqi(self):
        """ test result build for QBEQI """
        expected = ['equalization_enabled=Enabled', 'equalization_time=30min', 'equalization_period=30days', 'equalization_max_current=80A', 'reserved1=021', 'equalization_voltage=55.4V', 'reserved2=224', 'equalization_over_time=30min', 'equalization_active=Inactive', 'equalization_elasped_time=234hours']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QBEQI"})
        command.command_definition = proto.get_command_definition('QBEQI')
        _result = command.build_result(raw_response=b"(1 030 030 080 021 55.40 224 030 0 0234y?\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    # def test_build_result_qbeqi_wrong_response(self):
    #     """ test result build for QBEQI - wrong response"""
    #     expected = []
    #     simple_formatter = SimpleFormat({"extra_info": False})
    #     device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
    #     command = Command.from_config({"command": "QBEQI"})
    #     command.command_definition = proto.get_command_definition('QBEQI')
    #     _result = command.build_result(raw_response=b"(00238800!J\r", protocol=proto)
    #     formatted_data = simple_formatter.format(command, _result, device_info)
    #     print(formatted_data)
    #     self.assertEqual(formatted_data, expected)

    def test_build_result_verfw(self):
        """ test result build for VERFW """
        expected = ['bluetooth_firmware_version=00238800']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "VERFW"})
        command.command_definition = proto.get_command_definition('VERFW')
        _result = command.build_result(raw_response=b"(00238800!J\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qvfw3(self):
        """ test result build for QVFW3 """
        expected = ['remote_cpu_firmware_version=00072.70']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QVFW3"})
        command.command_definition = proto.get_command_definition('QVFW3')
        _result = command.build_result(raw_response=b"(VERFW:00072.70\x53\xA7\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qt(self):
        """ test result build for QT """
        expected = ['device_time=20210726122606']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QT"})
        command.command_definition = proto.get_command_definition('QT')
        _result = command.build_result(raw_response=b"(20210726122606JF\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qoppt(self):
        """ test result build for QOPPT """
        expected = ['output_source_priority_00_hours=Solar + Utility', 'output_source_priority_01_hours=Solar + Utility', 'output_source_priority_02_hours=Solar + Utility', 'output_source_priority_03_hours=Solar + Utility', 'output_source_priority_04_hours=Solar + Utility', 'output_source_priority_05_hours=Solar + Utility', 'output_source_priority_06_hours=Solar + Utility', 'output_source_priority_07_hours=Solar + Utility', 'output_source_priority_08_hours=Solar + Utility', 'output_source_priority_09_hours=Solar + Utility', 'output_source_priority_10_hours=Solar + Utility', 'output_source_priority_11_hours=Solar + Utility', 'output_source_priority_12_hours=Solar + Utility', 'output_source_priority_13_hours=Solar + Utility', 'output_source_priority_14_hours=Solar + Utility', 'output_source_priority_15_hours=Solar + Utility', 'output_source_priority_16_hours=Solar + Utility', 'output_source_priority_17_hours=Solar + Utility', 'output_source_priority_18_hours=Solar + Utility', 'output_source_priority_19_hours=Solar + Utility', 'output_source_priority_20_hours=Solar + Utility', 'output_source_priority_21_hours=Solar + Utility', 'output_source_priority_22_hours=Solar + Utility', 'output_source_priority_23_hours=Solar + Utility', 'device_output_source_priority=Solar + Utility', 'selection_of_output_source_priority_order_1=Utility', 'selection_of_output_source_priority_order_2=Solar + Utility', 'selection_of_output_source_priority_order_3=Solar first']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QOPPT"})
        command.command_definition = proto.get_command_definition('QOPPT')
        _result = command.build_result(raw_response=b"(2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 0 2 1>>\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qchpt(self):
        """ test result build for QCHPT """
        expected = ['charger_source_priority_00_hours=Solar + Utility', 'charger_source_priority_01_hours=Solar + Utility', 'charger_source_priority_02_hours=Solar + Utility', 'charger_source_priority_03_hours=Solar + Utility', 'charger_source_priority_04_hours=Solar + Utility', 'charger_source_priority_05_hours=Solar + Utility', 'charger_source_priority_06_hours=Solar + Utility', 'charger_source_priority_07_hours=Solar + Utility', 'charger_source_priority_08_hours=Solar + Utility', 'charger_source_priority_09_hours=Solar + Utility', 'charger_source_priority_10_hours=Solar + Utility', 'charger_source_priority_11_hours=Solar + Utility', 'charger_source_priority_12_hours=Solar + Utility', 'charger_source_priority_13_hours=Solar + Utility', 'charger_source_priority_14_hours=Solar + Utility', 'charger_source_priority_15_hours=Solar + Utility', 'charger_source_priority_16_hours=Solar + Utility', 'charger_source_priority_17_hours=Solar + Utility', 'charger_source_priority_18_hours=Solar + Utility', 'charger_source_priority_19_hours=Solar + Utility', 'charger_source_priority_20_hours=Solar + Utility', 'charger_source_priority_21_hours=Solar + Utility', 'charger_source_priority_22_hours=Solar + Utility', 'charger_source_priority_23_hours=Solar + Utility', 'device_charger_source_priority=Solar + Utility', 'selection_of_charger_source_priority_order_1=Utility', 'selection_of_charger_source_priority_order_2=Solar + Utility', 'selection_of_charger_source_priority_order_3=Solar first']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QCHPT"})
        command.command_definition = proto.get_command_definition('QCHPT')
        _result = command.build_result(raw_response=b"(2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 0 2 1>>\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qdi(self):
        """ test result build for QDI """
        expected = ['ac_output_voltage=230.0V', 'ac_output_frequency=50.0Hz', 'max_ac_charging_current=30A', 'battery_under_voltage=44.0V', 'battery_float_charge_voltage=54.0V', 'battery_bulk_charge_voltage=56.4V', 'battery_recharge_voltage=46.0V', 'max_charging_current=60A', 'input_voltage_range=Appliance', 'output_source_priority=Utility first', 'charger_source_priority=Solar + Utility', 'battery_type=AGM', 'buzzer=enabled', 'power_saving=disabled', 'overload_restart=disabled', 'over_temperature_restart=disabled', 'lcd_backlight=enabled', 'primary_source_interrupt_alarm=enabled', 'record_fault_code=enabled', 'overload_bypass=disabled', 'lcd_reset_to_default=enabled', 'output_mode=single machine', 'battery_redischarge_voltage=54.0V', 'pv_ok_condition=As long as one unit of inverters has connect PV, parallel system will consider PV OK', 'pv_power_balance=PV input max power will be the sum of the max charged power and loads power', 'max_charging_time_at_cv=224min']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QDI"})
        command.command_definition = proto.get_command_definition('QDI')
        test_response = command.command_definition.test_responses[0]
        _result = command.build_result(raw_response=test_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qmod(self):
        """ test result build for QMOD """
        expected = ['device_mode=Standby']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QMOD"})
        command.command_definition = proto.get_command_definition('QMOD')
        test_response = command.command_definition.test_responses[0]
        _result = command.build_result(raw_response=test_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qpigs(self):
        """ test result build for QPIGS """
        expected = ['ac_input_voltage=227.2V', 'ac_input_frequency=50.0Hz', 'ac_output_voltage=230.3V', 'ac_output_frequency=50.0Hz', 'ac_output_apparent_power=829VA', 'ac_output_active_power=751W', 'ac_output_load=10%', 'bus_voltage=447V', 'battery_voltage=54.5V', 'battery_charging_current=20A', 'battery_capacity=83%', 'inverter_heat_sink_temperature=54°C', 'pv1_input_current=2.7A', 'pv1_input_voltage=323.6V', 'battery_voltage_from_scc=0.0V', 'battery_discharge_current=0A', 'is_sbu_priority_version_added=0', 'is_configuration_changed=0', 'is_scc_firmware_updated=0', 'is_load_on=1', 'is_battery_voltage_to_steady_while_charging=0', 'is_charging_on=1', 'is_scc_charging_on=1', 'is_ac_charging_on=0', 'battery_voltage_offset_for_fans_on_(10mv)=0V', 'eeprom_version=0', 'pv1_charging_power=879W', 'is_charging_to_float=0', 'is_switched_on=1', 'is_dustproof_installed=0']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QPIGS"})
        command.command_definition = proto.get_command_definition('QPIGS')
        test_response = command.command_definition.test_responses[0]
        _result = command.build_result(raw_response=test_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qpgs0(self):
        """ test result build for QPGS0 """
        expected = ['parallel_instance_number=Not valid', 'serial_number=92932105105315', 'work_mode=Battery Mode', 'fault_code=No fault', 'grid_voltage=0.0V', 'grid_frequency=0.0Hz', 'ac_output_voltage=230.0V', 'ac_output_frequency=50.0Hz', 'ac_output_apparent_power=989VA', 'ac_output_active_power=907W', 'load_percentage=12%', 'battery_voltage=53.2V', 'battery_charging_current=9A', 'battery_capacity=90%', 'pv1_input_voltage=349.8V', 'total_charging_current=9A', 'total_ac_output_apparent_power=989VA', 'total_output_active_power=907W', 'total_ac_output_percentage=11%', 'is_scc_ok=1', 'is_ac_charging=0', 'is_scc_charging=1', 'is_battery_over_voltage=0', 'is_battery_under_voltage=0', 'is_line_lost=1', 'is_load_on=1', 'is_configuration_changed=0', 'output_mode=single machine', 'charger_source_priority=Solar first', 'max_charger_current=100A', 'max_charger_range=120A', 'max_ac_charger_current=30A', 'pv1_input_current=2A', 'battery_discharge_current=0A', 'pv2_input_voltage=275.3V', 'pv2_input_current=2A']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QPGS0"})
        command.command_definition = proto.get_command_definition('QPGS0')
        test_response = command.command_definition.test_responses[0]
        _result = command.build_result(raw_response=test_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qpiws(self):
        """ test result build for QPIWS """
        expected = ['pv_loss_warning=0', 'inverter_fault=0', 'bus_over_fault=0', 'bus_under_fault=0', 'bus_soft_fail_fault=0', 'line_fail_warning=1', 'opv_short_warning=0', 'inverter_voltage_too_low_fault=0', 'inverter_voltage_too_high_fault=0', 'over_temperature_fault=0', 'fan_locked_fault=0', 'battery_voltage_to_high_fault=0', 'battery_low_alarm_warning=0', 'reserved=0', 'battery_under_shutdown_warning=0', 'battery_derating_warning=0', 'overload_fault=1', 'eeprom_fault=0', 'inverter_over_current_fault=0', 'inverter_soft_fail_fault=0', 'self_test_fail_fault=0', 'op_dc_voltage_over_fault=0', 'bat_open_fault=0', 'current_sensor_fail_fault=0', 'battery_short_fault=0', 'power_limit_warning=0', 'pv_voltage_high_warning=0', 'mppt_overload_fault=0', 'mppt_overload_warning=0', 'battery_too_low_to_charge_warning=0', 'battery_weak=0']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QPIWS"})
        command.command_definition = proto.get_command_definition('QPIWS')
        test_response = command.command_definition.test_responses[0]
        _result = command.build_result(raw_response=test_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qflag(self):
        """ test result build for QFLAG """
        expected = ['buzzer=enabled', 'lcd_reset_to_default=enabled', 'lcd_backlight=enabled', 'primary_source_interrupt_alarm=enabled', 'overload_bypass=disabled', 'solar_feed_to_grid=disabled', 'overload_restart=disabled', 'over_temperature_restart=disabled', 'record_fault_code=disabled']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QFLAG"})
        command.command_definition = proto.get_command_definition('QFLAG')
        test_response = command.command_definition.test_responses[0]
        _result = command.build_result(raw_response=test_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_pledc(self):
        """ test result build for PLEDC3123123123 """
        expected = ['set_led_color=Succeeded']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "PLEDC3123123123"})
        command.command_definition = proto.get_command_definition('PLEDC3123123123')
        test_response = command.command_definition.test_responses[1]
        _result = command.build_result(raw_response=test_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_pledb4(self):
        """ test result build for PLEDB4 """
        expected = ['set_led_brightness=Failed']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "PLEDB4"})
        command.command_definition = proto.get_command_definition('PLEDB4')
        test_response = command.command_definition.test_responses[0]
        _result = command.build_result(raw_response=test_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_pledt2(self):
        """ test result build for PLEDT2 """
        expected = ['set_led_total_number_of_colors=Succeeded']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "PLEDT2"})
        command.command_definition = proto.get_command_definition('PLEDT2')
        test_response = command.command_definition.test_responses[1]
        _result = command.build_result(raw_response=test_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_plede0(self):
        """ test result build for PLEDE0 """
        expected = ['disable_led_function=Succeeded']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "PLEDE0"})
        command.command_definition = proto.get_command_definition('PLEDE0')
        test_response = command.command_definition.test_responses[1]
        _result = command.build_result(raw_response=test_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_disable_led(self):
        """ test result build for disable_led """
        expected = ['disable_led_function=Succeeded']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "disable_led"})
        command.command_definition = proto.get_command_definition('disable_led')
        test_response = command.command_definition.test_responses[1]
        _result = command.build_result(raw_response=test_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_led_off(self):
        """ test result build for led=off """
        expected = ['disable_led_function=Succeeded']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "led=off"})
        command.command_definition = proto.get_command_definition('led=off')
        test_response = command.command_definition.test_responses[1]
        _result = command.build_result(raw_response=test_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_set_led_off(self):
        """ test result build for set_led=off """
        expected = ['disable_led_function=Succeeded']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "set_led=off"})
        command.command_definition = proto.get_command_definition('set_led=off')
        test_response = command.command_definition.test_responses[1]
        _result = command.build_result(raw_response=test_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_plede1(self):
        """ test result build for PLEDE1 """
        expected = ['enable_led_function=Succeeded']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "PLEDE1"})
        command.command_definition = proto.get_command_definition('PLEDE1')
        test_response = command.command_definition.test_responses[1]
        _result = command.build_result(raw_response=test_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_enable_led(self):
        """ test result build for enable_led """
        expected = ['enable_led_function=Succeeded']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "enable_led"})
        command.command_definition = proto.get_command_definition('enable_led')
        test_response = command.command_definition.test_responses[1]
        _result = command.build_result(raw_response=test_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_led_on(self):
        """ test result build for led=on """
        expected = ['enable_led_function=Succeeded']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "led=on"})
        command.command_definition = proto.get_command_definition('led=on')
        test_response = command.command_definition.test_responses[1]
        _result = command.build_result(raw_response=test_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_set_led_on(self):
        """ test result build for set_led=on """
        expected = ['enable_led_function=Succeeded']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "set_led=on"})
        command.command_definition = proto.get_command_definition('set_led=on')
        test_response = command.command_definition.test_responses[1]
        _result = command.build_result(raw_response=test_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_pledm1(self):
        """ test result build for PLEDM1 """
        expected = ['set_led_effect=Succeeded']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "PLEDM1"})
        command.command_definition = proto.get_command_definition('PLEDM1')
        test_response = command.command_definition.test_responses[1]
        _result = command.build_result(raw_response=test_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_pleds1(self):
        """ test result build for PLEDS1 """
        expected = ['set_led_speed=Succeeded']
        simple_formatter = SimpleFormat({"extra_info": False})
        device_info = DeviceInfo(name="name", serial_number="serial_number", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "PLEDS1"})
        command.command_definition = proto.get_command_definition('PLEDS1')
        test_response = command.command_definition.test_responses[1]
        _result = command.build_result(raw_response=test_response, protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)
    