from typing import Literal

from pydantic import Field

from . import NoExtraBaseModel


class DaemonConfig(NoExtraBaseModel):
    """ model/allowed elements for daemon section of config """
    type: None | Literal['systemd'] | Literal['initd']
    keepalive: None | int = Field(default=None)
