""" pydantic definitions for the powermon format config model
"""
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class BaseFormatConfig(BaseModel):
    """ model/allowed elements for base format config """
    type: Optional[str] = 'simple'
    tag: Optional[str] = None
    draw_lines: Optional[bool] = False
    keep_case: Optional[bool] = False
    remove_spaces: Optional[bool] = True
    extra_info: Optional[bool] = False
    excl_filter: Optional[str] = None
    filter: Optional[str] = None

    model_config = ConfigDict(extra='forbid')


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
