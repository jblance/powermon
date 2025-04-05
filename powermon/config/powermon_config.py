"""
pydantic definitions for the powermon config model
"""
from typing import List, Literal

from pydantic import Field

from . import NoExtraBaseModel
from .api_config import APIConfig
from .daemon_config import DaemonConfig
from .device_config import DeviceConfig
from .mqtt_config import MQTTConfig
from .command_config import CommandConfig


class PowermonConfig(NoExtraBaseModel):
    """ model/allowed elements for first level of config """
    device: DeviceConfig
    commands: List[CommandConfig]
    mqttbroker: None | MQTTConfig = Field(default=None)
    api: None | APIConfig = Field(default=None)
    daemon: None | DaemonConfig = Field(default=None)
    debuglevel: None | int | str = Field(default=None)  # If you put "debug" it translates to 10 then fails to load the config
    loop: None | int | Literal["once"] = Field(default=None)
