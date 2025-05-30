from typing import List
from pydantic import BaseModel, ConfigDict

from .outputs import OutputConfig
from .triggers import AtTriggerConfig, EveryTriggerConfig, LoopsTriggerConfig
from .instruction_types import InstructionType


class InstructionConfig(BaseModel):
    """ model/allowed elements for command section of config """
    command: str
    type: InstructionType = InstructionType.BASIC
    override: dict = {}
    trigger: LoopsTriggerConfig | AtTriggerConfig | EveryTriggerConfig = EveryTriggerConfig(every=5)
    outputs: List[OutputConfig] = [OutputConfig(type='screen')]

    model_config = ConfigDict(extra='forbid')
