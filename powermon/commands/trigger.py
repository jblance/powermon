""" commands / trigger/py """
import datetime
import logging
import time
from enum import StrEnum, auto  # pylint: disable=E0611

from pydantic import BaseModel

log = logging.getLogger("Trigger")


class TriggerType(StrEnum):
    """ enum of valid types of triggers """
    EVERY = auto()
    LOOPS = auto()
    AT = auto()
    ONCE = auto()
    DISABLED = auto()


class TriggerDTO(BaseModel):
    """ data transfer model for Trigger class """
    trigger_type: str
    value: str | int


class Trigger:
    """ the trigger class """
    DATE_FORMAT = "%d %b %Y %H:%M:%S"

    def __init__(self, trigger_type, value=None):
        self.trigger_type = trigger_type
        self.value = value
        self.togo = 0
        self.last_run : float | None = None
        self.next_run : float = self.determine_next_run()

    def to_dto(self):
        """ data transfer object for Trigger objects """
        return TriggerDTO(
            trigger_type=self.trigger_type,
            value=self.value
        )

    def __str__(self):
        return f"trigger: {self.trigger_type} {self.value} loops togo: {self.togo}"

    @classmethod
    def from_config(cls, config=None):
        """ build trigger object from config dict """
        if not config:
            # no trigger defined, default to every loop
            trigger_type = TriggerType.LOOPS
            value = 1
        elif TriggerType.EVERY in config:
            trigger_type = TriggerType.EVERY
            value = config.get(TriggerType.EVERY, 61)
        elif TriggerType.LOOPS in config:
            trigger_type = TriggerType.LOOPS
            value = config.get(TriggerType.LOOPS, 101)
        elif TriggerType.AT in config:
            trigger_type = TriggerType.AT
            value = config.get(TriggerType.AT, "12:01")
        elif TriggerType.ONCE in config:
            trigger_type = TriggerType.ONCE
            value = config.get(TriggerType.ONCE, 0)
        else:
            trigger_type = TriggerType.DISABLED
            value = None
        return cls(trigger_type=trigger_type, value=value)

    @classmethod
    def from_dto(cls, dto: TriggerDTO) -> "Trigger":
        """ build a trigger from a dto """
        return cls(trigger_type=dto.trigger_type, value=dto.value)

    def touch(self):
        """ update last and next run times """
        # store run time (as secs since epoch)
        self.last_run = time.time()
        # update next run time
        self.next_run = self.determine_next_run()

    def get_last_run(self) -> str:
        """ readible form of last_run """
        last_run_str = "Not yet run"
        if self.last_run is not None:
            last_run_str = time.strftime(Trigger.DATE_FORMAT, time.localtime(self.last_run))
        return last_run_str

    def get_next_run(self) -> str:
        """ readible form of next_run """
        next_run_str = "unknown"
        if self.next_run is not None:
            next_run_str = time.strftime(Trigger.DATE_FORMAT, time.localtime(self.next_run))
        return next_run_str

    def is_due(self) -> bool:
        """ determine if this trigger is due or not """
        # Store the time now
        now = time.time()
        match self.trigger_type:
            case TriggerType.DISABLED:
                return False
            case TriggerType.EVERY:
                if self.last_run is None:
                    return True  # if hasnt run, run now
                if self.next_run <= now:
                    return True
                return False
            case TriggerType.LOOPS:
                if self.togo <= 0:
                    self.togo = self.value
                    return True
                else:
                    self.togo -= 1
                    return False
            case TriggerType.AT:
                if self.next_run is None:
                    #log.warning("at type trigger failed to set next run for %s" % command)
                    return False
                if self.next_run <= now:
                    return True
                return False
            case TriggerType.ONCE:
                if int(self.value) == 0:
                    self.value = 1
                    return True
                else:
                    return False
            case _:
                #log.warning("no isDue set for %s" % command)
                return False

    def determine_next_run(self) -> float:
        """ calculate next_run value """
        match self.trigger_type:
            case TriggerType.EVERY:
                # triggers every xx seconds
                # if hasnt run, run now
                if self.last_run is None:
                    next_run = time.time()
                else:
                    next_run = self.last_run + self.value
            case TriggerType.AT:
                # triggers at specific time each day
                dt_today = datetime.datetime.now()
                dt_now = dt_today.time()
                at_time = datetime.time.fromisoformat(self.value)
                if dt_now < at_time:
                    # needs to run today at at_time
                    next_run = dt_today.replace(hour=at_time.hour, minute=at_time.minute, second=at_time.second, microsecond=0).timestamp()
                else:
                    # needs to run tomorrow at at_time
                    next_run = (dt_today.replace(hour=at_time.hour, minute=at_time.minute, second=at_time.second, microsecond=0) + datetime.timedelta(days=1)).timestamp()
            case _:
                next_run = None
        return next_run
