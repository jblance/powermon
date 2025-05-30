""" pydantic definitions for the powermon trigger config model
"""
from pydantic import BaseModel, ConfigDict


class LoopsTriggerConfig(BaseModel):
    """ model/allowed elements for 'loops' trigger config """
    loops: int

    model_config = ConfigDict(extra='forbid')


class AtTriggerConfig(BaseModel):
    """ model/allowed elements for 'at' trigger config """
    at: str

    model_config = ConfigDict(extra='forbid')


class EveryTriggerConfig(BaseModel):
    """ model/allowed elements for 'every' trigger config """
    every: int

    model_config = ConfigDict(extra='forbid')
