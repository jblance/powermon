from typing import Literal

from pydantic import Field

from . import NoExtraBaseModel
from .format_config_model import (BaseFormatConfig, BMSResponseFormatConfig, HassFormatConfig, JsonFormatConfig,
                                  MqttFormatConfig)


class OutputConfig(NoExtraBaseModel):
    """ model/allowed elements for output config """
    type: Literal['screen'] | Literal['mqtt'] | Literal['api_mqtt']
    topic: None | str = Field(default=None)
    format: None | str | BaseFormatConfig | HassFormatConfig | MqttFormatConfig | JsonFormatConfig | BMSResponseFormatConfig = Field(default=None)
