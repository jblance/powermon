import asyncio
from unittest import TestCase
from unittest.mock import Mock

from powermon import PowermonConfig
# from powermon.config.device_config import DeviceConfig
from powermon.config.port_config_model import TestPortConfig
from powermon.device import Device
from powermon.commands.command import Command
from powermon.outputs.abstractoutput import AbstractOutput
from powermon.ports import Port
from powermon.protocols import Protocol


class DeviceTest(TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.port = None
        self.device = None

    def test_if_output_processed_in_success_run(self):
        """
        Test if output process called in success command run
        """
        #self.port = Mock(spec=SerialPort, protocol=PI30())
        port_config = TestPortConfig(type='test', protocol='pi30')

        # device_config = DeviceConfig()
        _model = 'max'
        _protocol = Protocol.from_name(name=port_config.protocol, model=_model)
        powermon_config = PowermonConfig(devices=[{'name': "Test Device", 'serial_number': '1234546', 'model': _model, 'manufacturer': 'mppsolar', 'port':port_config, 'commands': []}])
        self.device = Device(powermon_config.devices[0])
        self.device.port = asyncio.run( Port.from_config(config=port_config, protocol=_protocol, serial_number=powermon_config.devices[0].serial_number))

        # Add command into command list with dueToRun=True to emulate running command
        output = Mock(spec=AbstractOutput)
        self.device.add_command(Mock(spec=Command, code="Q1", command_type=None, outputs=[output], dueToRun=Mock(return_value=True)))

        # Run main device loop. Expecting positive result
        # self.assertTrue(self.device.run())
        asyncio.run(self.device.run())
        output.process.assert_called()
