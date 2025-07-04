""" commands / trigger/py """
import logging
import time

# from ._types import TriggerType
from ._config import SecondsTriggerConfig, LoopsTriggerConfig, AtTriggerConfig

log = logging.getLogger("Trigger")


class Trigger:
    """ the trigger class """
    DATE_FORMAT = "%d %b %Y %H:%M:%S"

    def __init__(self):
        pass
        

    def __str__(self):
        return f"{self.__class__.__name__}"


    @staticmethod
    def from_config(config=None):
        """ build trigger object from config dict """   
        if not config:
            # no trigger defined, default to every loop
            from .trigger_loops import TriggerLoops
            return TriggerLoops(loops=1)
        if config == 'once':
            from .trigger_once import TriggerOnce
            return TriggerOnce()
        if config == 'disabled':
            from .trigger_disabled import TriggerDisabled
            return TriggerDisabled()
        match config:
            case SecondsTriggerConfig():
                from .trigger_seconds import TriggerSeconds
                return TriggerSeconds(seconds=config.seconds)
            case LoopsTriggerConfig():
                from .trigger_loops import TriggerLoops
                return TriggerLoops(loops=config.loops)
            case AtTriggerConfig():
                from .trigger_at import TriggerAt
                return TriggerAt(at=config.at)
            case _:
                print('config type', type(config))
                print('not implemented')
                return


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


    def determine_next_run(self) -> None | float:
        return None
