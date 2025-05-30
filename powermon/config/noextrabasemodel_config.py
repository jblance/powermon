from pydantic import BaseModel, ConfigDict

class NoExtraBaseModel(BaseModel):
    """ updated BaseModel with Extras forbidden """
    model_config = ConfigDict(extra='forbid')