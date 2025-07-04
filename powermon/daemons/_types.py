from enum import StrEnum, auto

class DaemonType(StrEnum):
    """ Daemon types implemented """
    DISABLED = auto()
    SIMPLE = auto()
    SYSTEMD = auto()
    INITD = auto()