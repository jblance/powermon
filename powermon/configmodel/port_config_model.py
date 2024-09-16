""" pydantic definitions for the powermon port config model
"""
from typing import Literal

from pydantic import BaseModel, Field
from powermon.configmodel import NoExtraBaseModel


class BlePortConfig(NoExtraBaseModel):
    """ model/allowed elements for ble port config """
    type: Literal["ble"]
    mac: str
    protocol: None | str
    victron_key: None | str = Field(default=None)


class SerialPortConfig(NoExtraBaseModel):
    """ model/allowed elements for serial port config """
    type: Literal["serial"]
    path: str
    baud: None | int = Field(default=None)
    protocol: None | str
    identifier: None | str = Field(default=None)


class UsbPortConfig(NoExtraBaseModel):
    """ model/allowed elements for usb port config """
    type: Literal["usb"]
    path: None | str
    protocol: None | str
    identifier: None | str = Field(default=None)


class TestPortConfig(NoExtraBaseModel):
    """ model/allowed elements for test port config """
    type: Literal["test"]
    response_number: None | int = Field(default=None)
    protocol: None | str = Field(default=None)
