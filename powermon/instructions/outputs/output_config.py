from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict

from .formatters import (
    BaseFormatConfig,
    BMSResponseFormatConfig,
    HassFormatConfig,
    JsonFormatConfig,
    MqttFormatConfig,
)


class OutputConfig(BaseModel):
    """ model/allowed elements for output config """
    type: Literal['screen'] | Literal['mqtt'] | Literal['api_mqtt']
    topic: Optional[str] = None
    format: None | str | BaseFormatConfig | HassFormatConfig | MqttFormatConfig | JsonFormatConfig | BMSResponseFormatConfig = None

    model_config = ConfigDict(extra='forbid')
