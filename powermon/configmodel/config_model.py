"""
pydantic definitions for the powermon config model
"""
from typing import List, Literal

from pydantic import Field

from powermon.configmodel import NoExtraBaseModel
from powermon.configmodel.format_config_model import BaseFormatConfig, HassFormatConfig, MqttFormatConfig, JsonFormatConfig, BMSResponseFormatConfig
from powermon.configmodel.port_config_model import TestPortConfig, SerialPortConfig, UsbPortConfig, BlePortConfig
from powermon.configmodel.trigger_config_model import LoopsTriggerConfig, AtTriggerConfig, EveryTriggerConfig


class DaemonConfig(NoExtraBaseModel):
    """ model/allowed elements for daemon section of config """
    type: None | Literal['systemd'] | Literal['initd']
    keepalive: None | int = Field(default=None)


class MQTTConfig(NoExtraBaseModel):
    """ model/allowed elements for mqtt broker section of config """
    name: str
    port: None | int = Field(default=None)
    username: None | str = Field(default=None)
    password: None | str = Field(default=None, repr=False)
    adhoc_topic: None | str = Field(default=None)
    adhoc_result_topic: None | str = Field(default=None)


class APIConfig(NoExtraBaseModel):
    """ model/allowed elements for api section of config """
    host: None | str = Field(default=None)
    port: None | int = Field(default=None)
    enabled: None | bool = Field(default=False)
    log_level: None | str = Field(default=None)
    announce_topic: None | str = Field(default=None)
    adhoc_topic: None | str = Field(default=None)
    refresh_interval: None | int = Field(default=None)


class OutputConfig(NoExtraBaseModel):
    """ model/allowed elements for output config """
    type: Literal['screen'] | Literal['mqtt'] | Literal['api_mqtt']
    topic: None | str = Field(default=None)
    format: None | str | BaseFormatConfig | HassFormatConfig | MqttFormatConfig | JsonFormatConfig | BMSResponseFormatConfig = Field(default=None)


class CommandConfig(NoExtraBaseModel):
    """ model/allowed elements for command section of config """
    command: str
    type: None | Literal["basic"] | Literal["templated"] = Field(default="basic")
    override: None | dict = Field(default=None)
    trigger: None | LoopsTriggerConfig | AtTriggerConfig | EveryTriggerConfig = Field(default=None)
    outputs: None | List[OutputConfig] | str = Field(default=None)


class DeviceConfig(NoExtraBaseModel):
    """ model/allowed elements for device section of config """
    name: None | str = Field(default=None)
    id: None | str | int = Field(default=None)              # to be depreciated, replaced by serial_number
    serial_number: None | str | int = Field(default=None)
    model: None | str = Field(default=None)
    manufacturer: None | str = Field(default=None)
    port: TestPortConfig | SerialPortConfig | UsbPortConfig | BlePortConfig


class BaseConfig(NoExtraBaseModel):
    """ model/allowed elements for first level of config """
    device: DeviceConfig
    commands: List[CommandConfig]
    mqttbroker: None | MQTTConfig = Field(default=None)
    api: None | APIConfig = Field(default=None)
    daemon: None | DaemonConfig = Field(default=None)
    debuglevel: None | int | str = Field(default=None)  # If you put "debug" it translates to 10 then fails to load the config
    loop: None | int | Literal["once"] = Field(default=None)


class ConfigModel(NoExtraBaseModel):
    """Entry point for config model"""
    config: BaseConfig
