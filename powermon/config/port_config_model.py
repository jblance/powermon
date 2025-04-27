""" pydantic definitions for the powermon port config model
"""
from typing import Literal, Optional

from pydantic import Field

from . import NoExtraBaseModel
from ..protocols import Protocol


class BlePortConfig(NoExtraBaseModel):
    """ model/allowed elements for ble port config """
    type: Literal["ble"]
    mac: str
    protocol: str = Protocol.DEFAULT
    victron_key: Optional[str] = Field(default=None, repr=False)


class SerialPortConfig(NoExtraBaseModel):
    """ model/allowed elements for serial port config """
    type: Literal["serial"]
    path: str = "/dev/ttyUSB0"
    baud: int = 2400
    protocol: str = Protocol.DEFAULT


class UsbPortConfig(NoExtraBaseModel):
    """ model/allowed elements for usb port config """
    type: Literal["usb"]
    path: str = "/dev/hidraw0"
    protocol: str = Protocol.DEFAULT


class TestPortConfig(NoExtraBaseModel):
    """ model/allowed elements for test port config """
    type: Literal["test"]
    response_number: Optional[int] = None
    protocol: str = Protocol.DEFAULT
