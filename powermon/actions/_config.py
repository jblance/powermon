from typing import List, Literal

from pydantic import BaseModel, ConfigDict

from ._types import ActionType
from .outputs import OutputConfig
from .triggers import AtTriggerConfig, SecondsTriggerConfig, LoopsTriggerConfig


class ActionConfig(BaseModel):
    """ model/allowed elements for command section of config """
    command: str
    type: ActionType = ActionType.BASIC
    override: dict = {}
    trigger: LoopsTriggerConfig | AtTriggerConfig | SecondsTriggerConfig | Literal['once'] | Literal['disabled'] = SecondsTriggerConfig(seconds=5)
    outputs: str | List[OutputConfig] = [OutputConfig(type='screen')]

    model_config = ConfigDict(extra='forbid')
