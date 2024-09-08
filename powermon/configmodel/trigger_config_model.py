""" pydantic definitions for the powermon trigger config model
"""
from powermon.configmodel import NoExtraBaseModel


class LoopsTriggerConfig(NoExtraBaseModel):
    """ model/allowed elements for 'loops' trigger config """
    loops: int


class AtTriggerConfig(NoExtraBaseModel):
    """ model/allowed elements for 'at' trigger config """
    at: str


class EveryTriggerConfig(NoExtraBaseModel):
    """ model/allowed elements for 'every' trigger config """
    every: int
