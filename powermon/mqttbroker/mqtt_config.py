from typing import Optional

from pydantic import Field

from ..config import NoExtraBaseModel


class MQTTConfig(NoExtraBaseModel):
    """ model/allowed elements for mqtt broker section of config """
    name: str = None
    port: int = 1883
    disabled: bool = False
    username: Optional[str] = None
    password: Optional[str] = Field(default=None, repr=False)
    adhoc_topic: Optional[str] = None
    adhoc_result_topic: Optional[str] = None
