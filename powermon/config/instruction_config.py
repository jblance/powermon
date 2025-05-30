from typing import List

from .noextrabasemodel_config import NoExtraBaseModel
from .output_config import OutputConfig
from .trigger_config import AtTriggerConfig, EveryTriggerConfig, LoopsTriggerConfig
from ..types import InstructionType


class InstructionConfig(NoExtraBaseModel):
    """ model/allowed elements for command section of config """
    command: str
    type: InstructionType = InstructionType.BASIC
    override: dict = {}
    trigger: LoopsTriggerConfig | AtTriggerConfig | EveryTriggerConfig = EveryTriggerConfig(every=5)
    outputs: List[OutputConfig] = [OutputConfig(type='screen')]
