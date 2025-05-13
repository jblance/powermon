""" device.py """
# import gettext
import logging
from typing import Optional

from pydantic import BaseModel, Field

from powermon import MqttBroker
from ..commands.command import Command, CommandDTO
from ..commands.result import Result
# from ..config.powermon_config import PowermonConfig
from ..config.device_config import DeviceConfig
from ..libs.errors import CommandDefinitionMissing
from ..outputformats import FormatterType, get_formatter
from ..outputs.abstractoutput import AbstractOutput
from ..ports import from_config as port_from_config
from ..ports.abstractport import AbstractPort, _AbstractPortDTO

# Set-up logger
log = logging.getLogger("Device")


class DeviceDTO(BaseModel):
    """ data transfer model for Device class """
    name: str = 'unnamed_device'
    serial_number: Optional[str] = Field(strict=False, default=None, coerce_numbers_to_str=True)
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    port: _AbstractPortDTO
    commands: list[CommandDTO]


class Device:
    """
    The device object has information about the device - the name, model and serial number of the device
    The object also defines the port and protocol that is used to communicate with the device
    """
    # def __init__(self, name: str, serial_number: str = "", model: str = "", manufacturer: str = "", port: AbstractPort = None):
    def __init__(self, config: DeviceConfig):
        self.name=config.name
        self.serial_number=config.serial_number
        self.model=config.model
        self.manufacturer=config.manufacturer
        self.port: AbstractPort = None
        self.commands: list[Command] = []
        self.mqtt_broker = None
        self.adhoc_commands: list = []

    def __str__(self):
        #return f"Device: {self.device_info.name}, {self.device_info.serial_number=}, " + \
        #    f"{self.device_info.model=}, {self.device_info.manufacturer=}, " + \
        return f"Device: {self.name=}, {self.serial_number=}, {self.model=}, {self.manufacturer=} {self.port=}, {self.mqtt_broker=}, commands:{self.commands}"

    def to_dto(self) -> DeviceDTO:
        """convert the Device to a Data Transfer Object"""
        commands = []
        command: Command
        for command in self.commands:
            commands.append(command.to_dto())
        return DeviceDTO(name=self.name, serial_number=self.serial_number, model=self.model, manufacturer=self.manufacturer, port=self.port.to_dto(), commands=commands)

    # @classmethod
    # async def from_config(cls, config: PowermonConfig):
    #     """build the object from a config dict"""
    #     if not config:
    #         log.warning(_("No device definition in config. Check configFile argument?"))
    #         return cls(name="unnamed")
    #     name = config.name
    #     model = config.model
    #     manufacturer = config.manufacturer
    #     serial_number = config.serial_number

    #     port_config = config.port
    #     # add serial number and model to config
    #     # port_config['serial_number'] = serial_number
    #     # port_config['model'] = model
    #     port = await port_from_config(port_config)

    #     # raise error if unable to configure port
    #     if not port:
    #         log.error("Invalid port config '%s' found", config)
    #         raise ConfigError(f"Invalid port config '{config}' found")

    #     return cls(name=name, serial_number=serial_number, model=model, manufacturer=manufacturer, port=port)

    @property
    def port(self) -> AbstractPort:
        """the port associated with this device"""
        return self._port

    @port.setter
    def port(self, value):
        log.debug("Setting port to: %s", value)
        self._port = value

    @property
    def mqtt_broker(self) -> MqttBroker:
        """ the mqtt_broker object """
        return self._mqtt_broker

    @mqtt_broker.setter
    def mqtt_broker(self, mqtt_broker):
        log.debug("Setting mqtt_broker to: %s", mqtt_broker)
        self._mqtt_broker = mqtt_broker
        # If we are setting an actual broker object also set callback for adhoc commands
        if isinstance(mqtt_broker, MqttBroker) and mqtt_broker.adhoc_topic is not None:
            log.info("Subscribing to adhoc_topic: %s", mqtt_broker.adhoc_topic)
            mqtt_broker.subscribe(topic=mqtt_broker.adhoc_topic, callback=self.adhoc_command_cb)

    def adhoc_command_cb(self, client, userdata, msg):
        """ callback for adhoc command messages """
        log.debug("received message on %s, with payload: %s", msg.topic, msg.payload)
        # build command object
        command_code = msg.payload.decode()
        adhoc_command = Command.from_code(command_code)
        adhoc_command.command_definition = self.port.protocol.get_command_definition(command_code)
        # add to adhoc queue
        log.info("adding adhoc command: %s", adhoc_command)
        self.adhoc_commands.append(adhoc_command)

    def add_command(self, command: Command) -> None:
        """add a command to the devices' list of commands

        Args:
            command (Command): Command object to add to list
        """
        if command is None:
            return
        # get command definition from protocol
        try:
            command.command_definition = self.port.protocol.get_command_definition(command.code)
        except CommandDefinitionMissing as ex:
            log.warning("Could not find a definition for command: %s", command.code)
            log.debug("Exception was %r", ex)
            return

        # append to commands list
        self.commands.append(command)
        log.debug("added command (%s), command list length: %i", command, len(self.commands))

    async def initialize(self):
        """Device initialization activities"""
        log.info("initializing device")

    async def finalize(self):
        """Device finalization activities"""
        log.info("finalizing device: %s", self.name)
        # close connection on port
        await self.port.disconnect()

    async def run_adhoc_commands(self):
        """ check for any adhoc commands in the queue and run them """
        # check for any adhoc commands
        while len(self.adhoc_commands) > 0:
            # get the oldest adhoc command
            adhoc_command = self.adhoc_commands.pop(0)
            # run command
            log.info("Running adhoc command: %s", adhoc_command)
            try:
                # run command
                result: Result = await self.port.run_command(adhoc_command)
                log.info("Got result: %s", result)
            except Exception as exception:  # pylint: disable=W0718
                # specific errors need to incorporated into Result as part of the processing
                # so any exceptions at this stage will be truely unexpected
                log.error("Error decoding result: %s", exception)
                raise exception
            # process result
            # Currently using JSON format, one message per parameter
            #   eg:  powermon/adhoc_commands QPI
            #        powermon/adhoc_results {"data_name": "protocol_id", "data_value": "PI30", "data_unit": ""}
            _formatter = get_formatter(FormatterType.JSON)({})
            # publish result
            payload = _formatter.format(command=None, result=result, device_info=None)
            log.debug("Payload: %s", payload)
            for item in payload:
                self.mqtt_broker.post_adhoc_result(item)

    async def run(self, force=False):
        """checks for commands to run and runs them"""
        # run any adhoc commands
        await self.run_adhoc_commands()

        # check for any commands in the queue
        if self.commands is None or len(self.commands) == 0:
            log.info("no commands in queue")
            return

        for command in self.commands:
            if force or command.is_due():
                log.info("Running command: %s", command)
                try:
                    match command.command_type:
                        case 'cache_query':
                            print(command.command_type)
                            result: Result = None
                        case _:
                            # run command
                            result: Result = await self.port.run_command(command)
                    log.info("Got result: %s", result)
                except Exception as exception:  # pylint: disable=W0718
                    # specific errors need to incorporated into Result as part of the processing
                    # so any exceptions at this stage will be truely unexpected
                    log.error("Error decoding result: %s", exception)
                    raise exception

                # loop through each output and process result
                output: AbstractOutput
                for output in command.outputs:
                    log.debug("Using Output: %s", output)
                    output.process(command=command, result=result, device=self)
