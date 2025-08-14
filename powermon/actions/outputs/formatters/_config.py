""" pydantic definitions for the powermon format config model
"""
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class BaseFormatConfig(BaseModel):
    """ model/allowed elements for base format config """
    type: Optional[Literal['table', 'simple','raw']] = 'simple'
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
    type: Literal['hass']
    discovery_prefix: None | str = Field(default='homeassistant')
    entity_id_prefix: None | str = Field(default=None)


class JsonFormatConfig(BaseFormatConfig):
    """ model/allowed elements for mqtt format config """
    type: Literal['json']
    format: Optional[Literal['basic']] = 'basic'
    include_missing: Optional[bool] = False

class BMSResponseFormatConfig(BaseFormatConfig):
    """ model/allowed elements for BMSResponse format config """
    type: Literal['bmsresponse']
    protocol: None | Literal['pi30'] = Field(default=None)
    force_charge: None | bool = Field(default=None)
    battery_charge_voltage: None | float = Field(default=None)
    battery_float_voltage: None | float = Field(default=None)
    battery_cutoff_voltage: None | float = Field(default=None)
    battery_max_charge_current: None | int = Field(default=None)
    battery_max_discharge_current: None | int = Field(default=None)
