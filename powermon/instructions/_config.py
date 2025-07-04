from typing import List, Literal

from pydantic import BaseModel, ConfigDict

from ._types import InstructionType
from .outputs import OutputConfig
from .triggers import AtTriggerConfig, SecondsTriggerConfig, LoopsTriggerConfig


class InstructionConfig(BaseModel):
    """ model/allowed elements for command section of config """
    command: str
    type: InstructionType = InstructionType.BASIC
    override: dict = {}
    trigger: LoopsTriggerConfig | AtTriggerConfig | SecondsTriggerConfig | Literal['once'] | Literal['disabled'] = SecondsTriggerConfig(seconds=5)
    outputs: str | List[OutputConfig] = [OutputConfig(type='screen')]

    model_config = ConfigDict(extra='forbid')
