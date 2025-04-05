from pydantic import Field

from . import NoExtraBaseModel

class MQTTConfig(NoExtraBaseModel):
    """ model/allowed elements for mqtt broker section of config """
    name: str
    port: None | int = Field(default=None)
    username: None | str = Field(default=None)
    password: None | str = Field(default=None, repr=False)
    adhoc_topic: None | str = Field(default=None)
    adhoc_result_topic: None | str = Field(default=None)