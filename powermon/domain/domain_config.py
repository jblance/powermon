"""
pydantic definitions for the device config model
"""
from typing import List, Optional, Literal

from pydantic import BaseModel, ConfigDict, Field

from powermon.outputs import OutputConfig
from powermon.ports import (
    BlePortConfig,
    MockPortConfig,
    SerialPortConfig,
    UsbPortConfig,
)

from .domain_types import TaskType


class AtTriggerConfig(BaseModel):
    """ model/allowed elements for 'at' trigger config """
    at: str

    model_config = ConfigDict(extra='forbid')


class SecondsTriggerConfig(BaseModel):
    """ model/allowed elements for 'seconds' trigger config """
    seconds: int

    model_config = ConfigDict(extra='forbid')


class TaskConfig(BaseModel):
    """ model/allowed elements for command section of config """
    command: str
    type: TaskType = TaskType.BASIC
    override: dict = {}
    trigger:  AtTriggerConfig | SecondsTriggerConfig | Literal['once'] | Literal['disabled'] = SecondsTriggerConfig(seconds=5)
    outputs: str | List[OutputConfig] = [OutputConfig(type='screen')]

    model_config = ConfigDict(extra='forbid')


class DeviceConfig(BaseModel):
    """ model/allowed elements for device section of config """
    name: str = 'unnamed_device'
    serial_number: Optional[str] = Field(strict=False, default=None, coerce_numbers_to_str=True)
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    port: MockPortConfig | SerialPortConfig | UsbPortConfig | BlePortConfig
    tasks: List[TaskConfig]

    model_config = ConfigDict(extra='forbid')







