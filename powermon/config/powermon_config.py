"""
pydantic definitions for the powermon config model
"""
from typing import List, Literal  # , Optional

from pydantic import Field

from . import NoExtraBaseModel
from .api_config import APIConfig
from .daemon_config import DaemonConfig
from .device_config import DeviceConfig
from ..mqttbroker.mqtt_config import MQTTConfig
from .command_config import CommandConfig


class PowermonConfig(NoExtraBaseModel):
    """ model/allowed elements for first level of config """
    device: DeviceConfig
    commands: List[CommandConfig]
    mqttbroker: MQTTConfig = MQTTConfig()
    api: None | APIConfig = Field(default=None)
    daemon: None | DaemonConfig = Field(default=None)
    debuglevel: int | str = 'WARNING'
    loop: None | int | Literal["once"] = Field(default=None)
