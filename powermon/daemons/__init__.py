import logging
from enum import StrEnum, auto

from pydantic import BaseModel

from ..config.daemon_config import DaemonConfig


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
            print('disabled')
        case DaemonType.SIMPLE:
            print('simple')
        case DaemonType.SYSTEMD:
            print('systemd')
            from .daemon_systemd import DaemonSystemd as Daemon
            return Daemon(keepalive=config.keepalive)
        case DaemonType.INITD:
            print('initd')
        case _:
            print('Invalid daemon type')
    exit()
