from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MQTTConfig(BaseModel):
    """ model/allowed elements for mqtt broker section of config """
    name: Optional[str] = None
    port: int = 1883
    username: Optional[str] = None
    password: Optional[str] = Field(default=None, repr=False)
    adhoc_topic: Optional[str] = None
    adhoc_result_topic: Optional[str] = None

    model_config = ConfigDict(extra='forbid')
