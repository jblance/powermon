""" powermon / ports / __init__.py """
import logging
from enum import StrEnum, auto

from pydantic import BaseModel

from powermon.libs.errors import ConfigError


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

def from_config(port_config, serial_number=None):
    """ get a port object from config data """
    log.debug("port_config: %s", port_config)

    port_object = None
    if not port_config:
        raise ConfigError("no port config supplied")

    # port type is mandatory
    port_type = port_config.get("type")
    log.debug("portType: %s", port_type)

    # return None if port type is not defined
    if port_type is None:
        return None

    # add serial_number to config
    port_config['serial_number'] = serial_number

    # build port object
    match port_type:
        case PortType.TEST:
            from powermon.ports.testport import TestPort
            port_object = TestPort.from_config(config=port_config)
        case PortType.SERIAL:
            from powermon.ports.serialport import SerialPort
            port_object = SerialPort.from_config(config=port_config)
        case PortType.USB:
            from powermon.ports.usbport import USBPort
            port_object = USBPort.from_config(config=port_config)
        # Pattern for port types that cause problems when imported
        case PortType.BLE:
            log.debug("port_type BLE found")
            from powermon.ports.bleport import BlePort
            port_object = BlePort.from_config(config=port_config)
        case _:
            log.info("port type object not found for %s", port_type)
            raise ConfigError(f"Invalid port type: '{port_type}'")

    return port_object
