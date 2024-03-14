""" powermon / ports / porttype.py """
from enum import StrEnum, auto

from pydantic import BaseModel


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
    port_type: str
