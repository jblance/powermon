from typing import List, Literal

from pydantic import Field

from . import NoExtraBaseModel
from .output_config import OutputConfig
from .trigger_config_model import AtTriggerConfig, EveryTriggerConfig, LoopsTriggerConfig


class CommandConfig(NoExtraBaseModel):
    """ model/allowed elements for command section of config """
    command: str
    type: None | Literal["basic"] | Literal["templated"] | Literal["cache_query"] = Field(default="basic")
    override: None | dict = Field(default=None)
    trigger: None | LoopsTriggerConfig | AtTriggerConfig | EveryTriggerConfig = Field(default=None)
    outputs: None | List[OutputConfig] | str = Field(default=None)
