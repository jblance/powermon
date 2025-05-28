""" powermon / ports / __init__.py """
import logging
from enum import StrEnum, auto

from pydantic import BaseModel

from powermon.libs.errors import ConfigError
# from .abstractport import AbstractPort
from ..protocols import Protocol


# Set-up logger
log = logging.getLogger("ports")


class PortType(StrEnum):
    """ enumeration of supported / known port types """
    UNKNOWN = auto()
    TEST = auto()
    SERIAL = auto()
    USB = auto()
    BLE = auto()

    JKBLE = auto()
    MQTT = auto()
    VSERIAL = auto()
    DALYSERIAL = auto()
    ESP32 = auto()

class PortTypeDTO(BaseModel):
    """ data transfer model for PortType class """
    port_type: PortType


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
                from powermon.ports.testport import TestPort
                port_object: TestPort = await TestPort.from_config(config=config, protocol=protocol, serial_number=serial_number)
            case PortType.SERIAL:
                from powermon.ports.serialport import SerialPort
                port_object: SerialPort = await SerialPort.from_config(config=config, protocol=protocol, serial_number=serial_number)
            case PortType.USB:
                from powermon.ports.usbport import USBPort
                port_object: USBPort = await USBPort.from_config(config=config, protocol=protocol, serial_number=serial_number)
            # Pattern for port types that cause problems when imported
            case PortType.BLE:
                from powermon.ports.bleport import BlePort
                port_object: BlePort = await BlePort.from_config(config=config, protocol=protocol, serial_number=serial_number)
            case _:
                log.info("port type object not found for %s", port_type)
                raise ConfigError(f"Invalid port type: '{port_type}'")

        return port_object
