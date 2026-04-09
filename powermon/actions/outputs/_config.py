from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict

from .formatters import (
    BaseFormatConfig,
    BMSResponseFormatConfig,
    HassFormatConfig,
    JsonFormatConfig,
)


class OutputConfig(BaseModel):
    """ model/allowed elements for output config """
    type: Literal['screen'] | Literal['mqtt']
    topic: Optional[str] = None
    format: Optional[BaseFormatConfig | HassFormatConfig  | JsonFormatConfig | BMSResponseFormatConfig] = BaseFormatConfig()

    model_config = ConfigDict(extra='forbid')
