import logging
from enum import StrEnum, auto

from pydantic import BaseModel

from ..config.daemon_config import DaemonConfig

# Set-up logger
log = logging.getLogger("daemon_systemd")


class DaemonType(StrEnum):
    """ Daemon types implemented """
    DISABLED = auto()
    SIMPLE = auto()
    SYSTEMD = auto()
    INITD = auto()


class DaemonDTO(BaseModel):
    """ data transfer ojbect model """
    daemon_type: DaemonType
    enabled: bool
    keepalive: int


def from_config(config: DaemonConfig):
    match config.type:
        case DaemonType.DISABLED | None:
            from .daemon_disabled import DaemonDisabled as Daemon
        case DaemonType.SIMPLE:
            from .daemon_simple import DaemonSimple as Daemon
        case DaemonType.SYSTEMD:
            from .daemon_systemd import DaemonSystemd as Daemon
        case DaemonType.INITD:
            from .daemon_initd import DaemonInitd as Daemon
        case _:
            log.error('Invalid daemon type: %s', config.type)
            return
    return Daemon(keepalive=config.keepalive)
