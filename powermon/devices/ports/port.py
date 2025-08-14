""" powermon / ports / __init__.py """
import logging
from abc import abstractmethod

from powermon.exceptions import ConfigError, PowermonProtocolError

from ...protocols import Protocol
# from ...protocols.abstractprotocol import AbstractProtocol
from ._types import PortType

# Set-up logger
log = logging.getLogger("ports")


class Port():
    @staticmethod
    async def from_device_config(config=None):
        """ get a port object from config data - builds protocol object as well"""
        log.debug("device_config: %s", config)
        
        if not config:
            raise ConfigError("no device config supplied")

        protocol = Protocol.from_device_config(config=config)

        return await Port.from_config(config=config.port, protocol=protocol, serial_number=config.serial_number)

    @staticmethod
    async def from_config(config=None, protocol=None, serial_number=None):
        """ get a port object from config data """
        log.debug("port_config: %s", config)

        port_object = None
        if not config:
            raise ConfigError("no port config supplied")

        if protocol is None:
            raise ConfigError("no protocol supplied to Port.from_config")

        # port type is mandatory
        port_type = config.type
        log.debug("portType: %s", port_type)

        # return None if port type is not defined
        if port_type is None:
            return None

        if isinstance(protocol, str):
            protocol = Protocol.from_name(name=protocol)
        

        # build port object
        match port_type:
            case PortType.TEST:
                from .testport import TestPort
                port_object: TestPort = await TestPort.from_config(config=config, protocol=protocol, serial_number=serial_number)
            case PortType.SERIAL:
                from .serialport import SerialPort
                port_object: SerialPort = await SerialPort.from_config(config=config, protocol=protocol, serial_number=serial_number)
            case PortType.USB:
                from .usbport import USBPort
                port_object: USBPort = await USBPort.from_config(config=config, protocol=protocol, serial_number=serial_number)
            case PortType.BLE:
                from .bleport import BlePort
                port_object: BlePort = await BlePort.from_config(config=config, protocol=protocol, serial_number=serial_number)
            case _:
                log.info("port type object not found for %s", port_type)
                raise ConfigError(f"Invalid port type: '{port_type}'")

        return port_object

    def __init__(self, protocol):
        if isinstance(protocol, str):
            protocol = Protocol.from_name(name=protocol)
        self.protocol = protocol
        self.error_message = None
        # self.port_type = None
        self.is_protocol_supported()

    def is_protocol_supported(self):
        """ function to check if the protocol is supported by this port """
        port_type = getattr(self, "port_type", None)
        if port_type is None:
            raise PowermonProtocolError("Port type not defined")
        if port_type not in self.protocol.supported_ports:
            raise PowermonProtocolError(f"Protocol {self.protocol.protocol_id.decode()} not supported by port type {port_type}")

    async def connect(self) -> bool:
        """ default port connect function """
        log.debug("Port connect not implemented")
        return False


    async def disconnect(self) -> None:
        """ default port disconnect function """
        log.debug("Port disconnect not implemented")


    @abstractmethod
    def is_connected(self) -> bool:
        """ default is_connected function """
        raise NotImplementedError

    @property
    def protocol(self):
        """ return the protocol associated with this port """
        return self._protocol


    @protocol.setter
    def protocol(self, value):
        log.debug("Setting protocol to: %s", value)
        self._protocol = value


    async def run_command(self, command: 'Command') -> 'Result':
        """ run_command takes a command object, runs the command and returns a result object (replaces process_command) """
        log.debug("Command %s", command)

        # open port if it is closed
        if not self.is_connected():
            if not await self.connect():
                raise ConnectionError(f"Unable to connect to port: {self.error_message}")
        # FIXME: what if still not connected....
        # should, log an error and wait to try to reconnect (increasing backoff times)

        # update run times and re- expand any template
        command.touch()
        # update full_command - add crc etc
        # updates every run incase something has changed
        command.full_command = self.protocol.get_full_command(command.code)

        # run the command via the 'send_and_receive port function
        result = await self.send_and_receive(command)
        log.debug("after send_and_receive: %s", result)
        return result

    async def execute_action(self, action) -> 'Result':
        """ takes an instruction, runs the command and returns a result object"""
        log.debug("Action %s", action)

        # open port if it is closed
        if not self.is_connected():
            if not await self.connect():
                raise ConnectionError(f"Unable to connect to port: {self.error_message}")
        # FIXME: what if still not connected....
        # should, log an error and wait to try to reconnect (increasing backoff times)

        # update trigger times
        action.trigger.touch()
        
        # update full_command - add crc etc
        # updates every run incase something has changed
        action.full_command = self.protocol.get_full_command(action.get_command())

        # run the command via the 'send_and_receive port function
        result = await self.send_and_receive(action)
        log.debug("after send_and_receive: %s", result)
        return result