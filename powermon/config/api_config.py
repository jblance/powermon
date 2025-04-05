from pydantic import Field

from . import NoExtraBaseModel

class APIConfig(NoExtraBaseModel):
    """ model/allowed elements for api section of config """
    host: None | str = Field(default=None)
    port: None | int = Field(default=None)
    enabled: None | bool = Field(default=False)
    log_level: None | str = Field(default=None)
    announce_topic: None | str = Field(default=None)
    adhoc_topic: None | str = Field(default=None)
    refresh_interval: None | int = Field(default=None)