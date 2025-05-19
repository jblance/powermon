""" daemon.py """
import logging
from abc import ABC, abstractmethod
from enum import StrEnum, auto
from typing import Optional

from pydantic import BaseModel

from . import DaemonConfig

# Set-up logger
log = logging.getLogger("daemon")

def daemon_from_config(config: DaemonConfig):
    match config.type:
        case DaemonType.DISABLED | None:
            from .daemon_disabled import DaemonDisabled as daemon
        case DaemonType.SIMPLE:
            from .daemon_simple import DaemonSimple as daemon
        case DaemonType.SYSTEMD:
            from .daemon_systemd import DaemonSystemd as daemon
        case DaemonType.INITD:
            from .daemon_initd import DaemonInitd as daemon
        case _:
            log.error('Invalid daemon type: %s', config.type)
            from .daemon_disabled import DaemonDisabled as daemon
    return daemon(keepalive=config.keepalive)


class DaemonType(StrEnum):
    """ Daemon types implemented """
    DISABLED = auto()
    SIMPLE = auto()
    SYSTEMD = auto()
    INITD = auto()


class DaemonDTO(BaseModel):
    """ data transfer ojbect model """
    daemon_type: DaemonType
    last_notify: Optional[int | float] = None
    keepalive: int


class Daemon(ABC):
    """ abstraction to support different daemon approaches / solutions """
    def __str__(self):
        return f"Daemon: {self.__class__=}, {self.keepalive=}, {self.last_notify}"


    def __init__(self, keepalive: int):
        self.type: DaemonType = None
        self.keepalive: int  = keepalive
        self.last_notify: Optional[int | float] = None


    @abstractmethod
    def initialize(self):
        raise NotImplementedError


    @abstractmethod
    def watchdog(self):
        raise NotImplementedError


    @abstractmethod
    def notify(self, status="OK"):
        raise NotImplementedError


    @abstractmethod
    def stop(self):
        raise NotImplementedError


    @abstractmethod
    def log(self, message=None):
        raise NotImplementedError


    def to_dto(self):
        """ return the data transfer object version of this object """
        return DaemonDTO(
            daemon_type=self.type,
            last_notify=self.last_notify,
            keepalive=self.keepalive,
        )
