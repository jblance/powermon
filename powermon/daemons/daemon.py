""" daemon.py """
import logging
from abc import ABC, abstractmethod

from . import DaemonDTO


# Set-up logger
log = logging.getLogger("daemon")


class Daemon(ABC):
    """ abstraction to support different daemon approaches / solutions """
    def __str__(self):
        return f"Daemon: {self.__class__=}, {self.keepalive=}, {self.last_notify}"


    def __init__(self, keepalive):
        self.type = None
        self.keepalive = keepalive
        self.last_notify = None


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
