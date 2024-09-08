""" pydantic definitions for the powermon port config model
"""
from typing import Literal

from pydantic import BaseModel, Field


class BlePortConfig(BaseModel):
    """ model/allowed elements for serial port config """
    type: Literal["ble"]
    mac: str
    protocol: None | str


class SerialPortConfig(BaseModel):
    """ model/allowed elements for serial port config """
    type: Literal["serial"]
    path: str
    baud: None | int = Field(default=None)
    protocol: None | str


class UsbPortConfig(BaseModel):
    """ model/allowed elements for usb port config """
    type: Literal["usb"]
    path: None | str
    protocol: None | str


class TestPortConfig(BaseModel):
    """ model/allowed elements for test port config """
    type: Literal["test"]
    response_number: None | int = Field(default=None)
    protocol: None | str = Field(default=None)
