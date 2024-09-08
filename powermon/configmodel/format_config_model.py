""" pydantic definitions for the powermon format config model
"""
from typing import Literal

from pydantic import Field

from powermon.configmodel import NoExtraBaseModel


class BaseFormatConfig(NoExtraBaseModel):
    """ model/allowed elements for base format config """
    type: str
    tag: None | str = Field(default=None)
    draw_lines: None | bool = Field(default=None)
    keep_case: None | bool = Field(default=None)
    remove_spaces: None | bool = Field(default=None)
    extra_info: None | bool = Field(default=None)
    excl_filter: None | str = Field(default=None)
    filter: None | str = Field(default=None)


class HassFormatConfig(BaseFormatConfig):
    """ model/allowed elements for hass format config """
    discovery_prefix: None | str = Field(default=None)
    entity_id_prefix: None | str = Field(default=None)


class MqttFormatConfig(BaseFormatConfig):
    """ model/allowed elements for mqtt format config """
    topic: None | str


class JsonFormatConfig(BaseFormatConfig):
    """ model/allowed elements for mqtt format config """
    format: None | str
    include_missing: None | bool = Field(default=None)

class BMSResponseFormatConfig(BaseFormatConfig):
    """ model/allowed elements for BMSResponse format config """
    protocol: None | Literal['pi30'] = Field(default=None)
    force_charge: None | bool = Field(default=None)
    battery_charge_voltage: None | float = Field(default=None)
    battery_float_voltage: None | float = Field(default=None)
    battery_cutoff_voltage: None | float = Field(default=None)
    battery_max_charge_current: None | int = Field(default=None)
    battery_max_discharge_current: None | int = Field(default=None)
