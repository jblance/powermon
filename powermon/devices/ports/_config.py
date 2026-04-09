""" pydantic definitions for the powermon port config model
"""
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from ...protocols import ProtocolType


class BlePortConfig(BaseModel):
    """ model/allowed elements for ble port config """
    type: Literal["ble"] = 'ble'
    mac: str
    protocol: ProtocolType = ProtocolType.DEFAULT
    victron_key: Optional[str] = Field(default=None, repr=False)

    model_config = ConfigDict(extra='forbid')


class SerialPortConfig(BaseModel):
    """ model/allowed elements for serial port config """
    type: Literal["serial"] = 'serial'
    path: str = "/dev/ttyUSB0"
    baud: int = 2400
    protocol: ProtocolType = ProtocolType.DEFAULT

    model_config = ConfigDict(extra='forbid')


class UsbPortConfig(BaseModel):
    """ model/allowed elements for usb port config """
    type: Literal["usb"] = 'usb'
    path: str = "/dev/hidraw0"
    protocol: ProtocolType = ProtocolType.DEFAULT

    model_config = ConfigDict(extra='forbid')


class TestPortConfig(BaseModel):
    """ model/allowed elements for test port config """
    type: Literal["test"] = 'test'
    response_number: Optional[int] = None
    protocol: ProtocolType = ProtocolType.DEFAULT

    model_config = ConfigDict(extra='forbid')
