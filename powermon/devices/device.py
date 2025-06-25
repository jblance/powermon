""" device.py """
# import gettext
import logging
from typing import List, Optional

from ..commands.result import Result
from .device_config import DeviceConfig
from ..instructions import Instruction
from ..mqttbroker import MqttBroker
# from ..instructions.outputs.formatters import FormatterType
from ..instructions.outputs.abstractoutput import AbstractOutput
from .ports import Port
from .ports.abstractport import AbstractPort

# Set-up logger
log = logging.getLogger("Device")


class Device:
    """
    The device object has information about the device - the name, model and serial number of the device
    The object also defines the port and protocol that is used to communicate with the device
    """
    # def __init__(self, name: str, serial_number: str = "", model: str = "", manufacturer: str = "", port: AbstractPort = None):
    @classmethod
    async def from_config(cls, config: DeviceConfig):
        _device: Device = cls(name=config.name, serial_number=config.serial_number, model=config.model, manufacturer=config.manufacturer)
        _device.config = config
        _device.port = await Port.from_device_config(config=config)
        return _device


    def __init__(self, name: str, serial_number: str, model: str, manufacturer: str, port: Optional[AbstractPort] = None, instructions: Optional[List[Instruction]] = None, mqtt_broker: Optional[MqttBroker] = None):
        self.config: DeviceConfig = None
        self.name: str = name
        self.serial_number: str = serial_number
        self.model: str = model
        self.manufacturer: str = manufacturer
        self.port: AbstractPort = port
        self.instructions: list[Instruction] = [] if instructions is None else instructions
        self.mqtt_broker: MqttBroker = mqtt_broker
        self.adhoc_commands: list = []

    def __str__(self):
        return f"Device: {self.name=}, {self.serial_number=}, {self.model=}, {self.manufacturer=} {self.port=}, {self.mqtt_broker=}, instructions:{self.instructions}"


    def __repr__(self):
        """ Returns representation of Device that allows eval(device.__repr__()) to rebuild object"""
        _repr = f"Device(name='{self.name}', serial_number='{self.serial_number}', model='{self.model}', manufacturer='{self.manufacturer}', port={self.port!r}, instructions={self.instructions})"
        #print(_repr)
        return _repr


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


    def add_instruction(self, instruction: Instruction) -> None:
        """ add instruction to list of instructions """
        if instruction is None:
            return
        # do instruction processing - eg find definition
        #
        self.instructions.append(instruction)


    # def add_command(self, command: 'Command') -> None:
    #     """add a command to the devices' list of commands

    #     Args:
    #         command (Command): Command object to add to list
    #     """
    #     if command is None:
    #         return
    #     # get command definition from protocol
    #     try:
    #         command.command_definition = self.port.protocol.get_command_definition(command.code)
    #     except CommandDefinitionMissing as ex:
    #         log.warning("Could not find a definition for command: %s", command.code)
    #         log.debug("Exception was %r", ex)
    #         return

    #     # append to commands list
    #     self.commands.append(command)
    #     log.debug("added command (%s), command list length: %i", command, len(self.commands))

    async def initialize(self):
        """Device initialization activities"""
        log.info("initializing device")

    async def finalize(self):
        """Device finalization activities"""
        log.info("finalizing device: %s", self.name)
        # close connection on port
        await self.port.disconnect()

    # async def run_adhoc_commands(self):
    #     """ check for any adhoc commands in the queue and run them """
    #     # check for any adhoc commands
    #     while len(self.adhoc_commands) > 0:
    #         # get the oldest adhoc command
    #         adhoc_command = self.adhoc_commands.pop(0)
    #         # run command
    #         log.info("Running adhoc command: %s", adhoc_command)
    #         try:
    #             # run command
    #             result: Result = await self.port.run_command(adhoc_command)
    #             log.info("Got result: %s", result)
    #         except Exception as exception:  # pylint: disable=W0718
    #             # specific errors need to incorporated into Result as part of the processing
    #             # so any exceptions at this stage will be truely unexpected
    #             log.error("Error decoding result: %s", exception)
    #             raise exception
    #         # process result
    #         # Currently using JSON format, one message per parameter
    #         #   eg:  powermon/adhoc_commands QPI
    #         #        powermon/adhoc_results {"data_name": "protocol_id", "data_value": "PI30", "data_unit": ""}
    #         _formatter = get_formatter(FormatterType.JSON)({})
    #         # publish result
    #         payload = _formatter.format(command=None, result=result, device_info=None)
    #         log.debug("Payload: %s", payload)
    #         for item in payload:
    #             self.mqtt_broker.post_adhoc_result(item)

    async def run(self, force=False):
        """checks for commands to run and runs them"""
        # run any adhoc commands
        # await self.run_adhoc_commands()

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
                            result: Result = None  # ty: ignore[invalid-assignment]
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
