"""
Pydantic definitions for the powermon config model (schema v2).
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .daemons import DaemonConfig
from .domain import DeviceConfig
from .mqttbroker import MQTTConfig


class PowermonConfig(BaseModel):
    """Top-level powermon configuration schema."""
    config_version: Literal[2] = 2
    devices: list[DeviceConfig]

    mqttbroker: MQTTConfig = Field(default_factory=MQTTConfig)
    daemon: DaemonConfig = Field(default_factory=DaemonConfig)

    model_config = ConfigDict(extra="forbid")
