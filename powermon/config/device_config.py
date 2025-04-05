from pydantic import Field

from . import NoExtraBaseModel

from .port_config_model import BlePortConfig, SerialPortConfig, TestPortConfig, UsbPortConfig

class DeviceConfig(NoExtraBaseModel):
    """ model/allowed elements for device section of config """
    name: None | str = Field(default=None)
    id: None | str | int = Field(default=None)              # to be depreciated, replaced by serial_number
    serial_number: None | str | int = Field(default=None)
    model: None | str = Field(default=None)
    manufacturer: None | str = Field(default=None)
    port: TestPortConfig | SerialPortConfig | UsbPortConfig | BlePortConfig
