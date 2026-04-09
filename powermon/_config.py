"""
pydantic definitions for the powermon config model
"""
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from .daemons import DaemonConfig
from .devices import DeviceConfig
from .mqttbroker import MQTTConfig


class PowermonConfig(BaseModel):
    """ model/allowed elements for first level of config (version 2)"""
    devices: List[DeviceConfig]
    mqttbroker: MQTTConfig = MQTTConfig()
    daemon: DaemonConfig = DaemonConfig()
    debuglevel: int | str = 'WARNING'
    loop: Optional[int] = None

    model_config = ConfigDict(extra='forbid')
