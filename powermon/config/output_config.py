from typing import Literal, Optional

from .noextrabasemodel_config import NoExtraBaseModel
from .format_config import (BaseFormatConfig, BMSResponseFormatConfig, HassFormatConfig, JsonFormatConfig,
                                  MqttFormatConfig)


class OutputConfig(NoExtraBaseModel):
    """ model/allowed elements for output config """
    type: Literal['screen'] | Literal['mqtt'] | Literal['api_mqtt']
    topic: Optional[str] = None
    format: None | str | BaseFormatConfig | HassFormatConfig | MqttFormatConfig | JsonFormatConfig | BMSResponseFormatConfig = None
