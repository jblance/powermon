from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DaemonConfig(BaseModel):
    """ model/allowed elements for daemon section of config """
    type: None | Literal['disabled'] | Literal['simple'] | Literal['systemd'] | Literal['initd'] = Field(default=None)
    keepalive: None | int = Field(default=None)

    model_config = ConfigDict(extra='forbid')
