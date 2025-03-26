""" tests / integration / test_cmd_powermon_pi30.py """
import subprocess
import unittest


class test_command_line_powermon(unittest.TestCase):
    maxDiff = 9999

    def test_run_powermon_qpi_cmd(self):
        try:
            expected = "protocol_id=PI30\n"
            result = subprocess.run(
                ["powermon", "--once", "--config", '{"device": {"port":{"type":"test"}}, "commands": [{"command":"QPI"}]}'],
                check=True,
                capture_output=True,
                text=True,
            )
            # print(result.stdout)
            self.assertEqual(result.stdout, expected)
            self.assertEqual(result.returncode, 0)
        except subprocess.CalledProcessError as error:
            print(error.stdout)
            print(error.stderr)
            raise error

    def test_run_powermon_output1(self):
        try:
            expected = "protocol_id=PI30\n"
            result = subprocess.run(
                [
                    "powermon",
                    "--once",
                    "--config",
                    '{"device": {"port":{"type":"test"}}, "commands": [{"command": "QPI", "outputs": [{"type": "screen", "format": "simple"}]}]}',
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            # print(result.stdout)
            self.assertEqual(result.stdout, expected)
            self.assertEqual(result.returncode, 0)
        except subprocess.CalledProcessError as error:
            print(error.stdout)
            print(error.stderr)
            raise error

    def test_run_powermon_many_output(self):
        try:
            expected = """ac_input_voltage=0.0V
ac_input_frequency=0.0Hz
ac_output_voltage=230.0V
ac_output_frequency=49.9Hz
ac_output_apparent_power=161VA
ac_output_active_power=119W
ac_output_load=3%
bus_voltage=460V
battery_voltage=57.5V
battery_charging_current=12A
battery_capacity=100%
inverter_heat_sink_temperature=69°C
pv_input_current=14.0A
pv_input_voltage=103.8V
battery_voltage_from_scc=57.45V
battery_discharge_current=0A
is_sbu_priority_version_added=0
is_configuration_changed=0
is_scc_firmware_updated=1
is_load_on=1
is_battery_voltage_to_steady_while_charging=0
is_charging_on=1
is_scc_charging_on=1
is_ac_charging_on=0
rsv1=0A
rsv2=0A
pv_input_power=856W
is_charging_to_float=0
is_switched_on=1
is_dustproof_installed=0
ac_input_voltage=0.0V
ac_input_frequency=0.0Hz
ac_output_voltage=230.0V
ac_output_frequency=49.9Hz
ac_output_apparent_power=161VA
ac_output_active_power=119W
ac_output_load=3%
bus_voltage=460V
battery_voltage=57.5V
battery_charging_current=12A
battery_capacity=100%
inverter_heat_sink_temperature=69°C
pv_input_current=14.0A
pv_input_voltage=103.8V
battery_voltage_from_scc=57.45V
battery_discharge_current=0A
is_sbu_priority_version_added=0
is_configuration_changed=0
is_scc_firmware_updated=1
is_load_on=1
is_battery_voltage_to_steady_while_charging=0
is_charging_on=1
is_scc_charging_on=1
is_ac_charging_on=0
rsv1=0A
rsv2=0A
pv_input_power=856W
is_charging_to_float=0
is_switched_on=1
is_dustproof_installed=0
protocol_id=PI30
device_mode=Standby\n"""
            result = subprocess.run(
                [
                    "powermon",
                    "--once",
                    "--config",
                    '{"commands": [{"command": "QPIGS", "type": "basic", "trigger": {"every": 25}, "outputs": [{"type": "screen", "format": "simple"}, {"type": "screen", "format": {"type": "simple"}}]}, {"command": "QPI", "outputs": [{"type": "screen", "format": "simple"}]}, {"command": "QID", "outputs": "screen", "trigger": {"at": "12:56"}}, {"command": "QMOD", "trigger": {"loops": 50}}], "device": {"port": {"type": "test", "response_number": 0}}}',
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            # print(result.stdout)
            self.assertEqual(result.stdout, expected)
            self.assertEqual(result.returncode, 0)
        except subprocess.CalledProcessError as error:
            print(error.stdout)
            print(error.stderr)
            raise error

    def test_run_powermon_QID(self):
        try:
            expected = "serial_number=9293333010501\n"
            result = subprocess.run(
                [
                    "powermon",
                    "--once",
                    "--config",
                    '{"device": {"port":{"type":"test"}}, "commands": [{"command": "QID", "outputs": [{"type": "screen", "format": "simple"}]}]}',
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            # print(result.stdout)
            self.assertEqual(result.stdout, expected)
            self.assertEqual(result.returncode, 0)
        except subprocess.CalledProcessError as error:
            print(error.stdout)
            print(error.stderr)
            raise error

    def test_run_powermon_QMCHGCR(self):
        try:
            expected = """max_charging_current_options=010 020 030 040 050 060 070 080 090 100 110 120A\n"""
            result = subprocess.run(
                [
                    "powermon",
                    "--once",
                    "--config",
                    '{"device": {"port":{"type":"test"}}, "commands": [{"command": "QMCHGCR", "outputs": [{"type": "screen", "format": "simple"}]}]}',
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            # print(result.stdout)
            self.assertEqual(result.stdout, expected)
            self.assertEqual(result.returncode, 0)
        except subprocess.CalledProcessError as error:
            print(error.stdout)
            print(error.stderr)
            raise error

    def test_run_powermon_QMOD(self):
        try:
            expected = "device_mode=Standby\n"
            result = subprocess.run(
                [
                    "powermon",
                    "--once",
                    "--config",
                    '{"device": {"port":{"type":"test", "response_number": 0}}, "commands": [{"command": "QMOD", "outputs": [{"type": "screen", "format": "simple"}]}]}',
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            # print(result.stdout)
            self.assertEqual(result.stdout, expected)
            self.assertEqual(result.returncode, 0)
        except subprocess.CalledProcessError as error:
            print(error.stdout)
            print(error.stderr)
            raise error

    def test_run_powermon_QMN(self):
        try:
            expected = "model_name=MKS2-8000\n"
            result = subprocess.run(
                [
                    "powermon",
                    "--once",
                    "--config",
                    '{"device": {"port":{"type":"test"}}, "commands": [{"command": "QMN", "outputs": [{"type": "screen", "format": "simple"}]}]}',
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            # print(result.stdout)
            self.assertEqual(result.stdout, expected)
            self.assertEqual(result.returncode, 0)
        except subprocess.CalledProcessError as error:
            print(error.stdout)
            print(error.stderr)
            raise error

    def test_run_powermon_QGMN(self):
        try:
            expected = "general_model_number=044\n"
            result = subprocess.run(
                [
                    "powermon",
                    "--once",
                    "--config",
                    '{"device": {"port":{"type":"test"}}, "commands": [{"command": "QGMN", "outputs": [{"type": "screen", "format": "simple"}]}]}',
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            # print(result.stdout)
            self.assertEqual(result.stdout, expected)
            self.assertEqual(result.returncode, 0)
        except subprocess.CalledProcessError as error:
            print(error.stdout)
            print(error.stderr)
            raise error

    def test_run_powermon_QMUCHGCR(self):
        try:
            expected = "max_utility_charging_current=002 010 020 030 040 050 060 070 080 090 100 110 120A\n"
            result = subprocess.run(
                [
                    "powermon",
                    "--once",
                    "--config",
                    '{"device": {"port":{"type":"test"}}, "commands": [{"command": "QMUCHGCR", "outputs": [{"type": "screen", "format": "simple"}]}]}',
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            # print(result.stdout)
            self.assertEqual(result.stdout, expected)
            self.assertEqual(result.returncode, 0)
        except subprocess.CalledProcessError as error:
            print(error.stdout)
            print(error.stderr)
            raise error

    def test_run_powermon_QOPM(self):
        try:
            expected = "output_mode=single machine\n"
            result = subprocess.run(
                [
                    "powermon",
                    "--once",
                    "--config",
                    '{"device": {"port":{"type":"test", "response_number": 0}}, "commands": [{"command": "QOPM", "outputs": [{"type": "screen", "format": "simple"}]}]}',
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            # print(result.stdout)
            self.assertEqual(result.stdout, expected)
            self.assertEqual(result.returncode, 0)
        except subprocess.CalledProcessError as error:
            print(error.stdout)
            print(error.stderr)
            raise error

    def test_run_powermon_QVFW(self):
        try:
            expected = "main_cpu_firmware_version=00072.70\n"
            result = subprocess.run(
                [
                    "powermon",
                    "--once",
                    "--config",
                    '{"device": {"port":{"type":"test"}}, "commands": [{"command": "QVFW", "outputs": [{"type": "screen", "format": "simple"}]}]}',
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            # print(result.stdout)
            self.assertEqual(result.stdout, expected)
            self.assertEqual(result.returncode, 0)
        except subprocess.CalledProcessError as error:
            print(error.stdout)
            print(error.stderr)
            raise error

    def test_run_powermon_QVFW2(self):
        try:
            expected = "secondary_cpu_firmware_version=00072.70\n"
            result = subprocess.run(
                [
                    "powermon",
                    "--once",
                    "--config",
                    '{"device": {"port":{"type":"test"}}, "commands": [{"command": "QVFW2", "outputs": [{"type": "screen", "format": "simple"}]}]}',
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            # print(result.stdout)
            self.assertEqual(result.stdout, expected)
            self.assertEqual(result.returncode, 0)
        except subprocess.CalledProcessError as error:
            print(error.stdout)
            print(error.stderr)
            raise error
