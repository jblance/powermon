from pydantic import BaseModel, Extra, Field


class NoExtraBaseModel(BaseModel):
    """ updated BaseModel with Extras forbidden """
    class Config:
        """pydantic BaseModel config"""
        extra = Extra.forbid
        