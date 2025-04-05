from typing import Optional

from pydantic import Field

from . import NoExtraBaseModel
from .port_config_model import BlePortConfig, SerialPortConfig, TestPortConfig, UsbPortConfig


class DeviceConfig(NoExtraBaseModel):
    """ model/allowed elements for device section of config """
    name: str = 'unnamed_device'
    serial_number: Optional[str] = Field(strict=False, default=None, coerce_numbers_to_str=True)
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    port: TestPortConfig | SerialPortConfig | UsbPortConfig | BlePortConfig
