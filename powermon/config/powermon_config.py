"""
pydantic definitions for the powermon config model
"""
from typing import List, Optional

# from pydantic import Field

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
    mqttbroker: MQTTConfig = MQTTConfig()
    api: APIConfig = APIConfig()
    daemon: DaemonConfig = DaemonConfig()
    debuglevel: int | str = 'WARNING'
    loop: Optional[int] = None
