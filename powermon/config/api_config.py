from typing import Optional

# from pydantic import Field

from .noextrabasemodel_config import NoExtraBaseModel


class APIConfig(NoExtraBaseModel):
    """ model/allowed elements for api section of config """
    host: Optional[str] = None
    port: Optional[int] = None
    enabled: Optional[bool] = False
    log_level: Optional[str] = None
    announce_topic: Optional[str] = None
    adhoc_topic: Optional[str] = None
    refresh_interval: Optional[int] = None
