""" powermon / ports / porttype.py """
from enum import Enum, auto
# from strenum import LowercaseStrEnum


class PortType(Enum):
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