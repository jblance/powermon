import time

from . import Trigger


class TriggerSeconds(Trigger):

    def __str__(self):
        return f"{self.__class__.__name__}: {self.seconds=}, last_run={self.get_last_run()}, next_run={self.get_next_run()}"


    def __init__(self, seconds):
        self.seconds = seconds
        self.last_run : float | None = None
        self.next_run : float = self.determine_next_run()

    
    def is_due(self) -> bool:
        """ determine if this trigger is due or not """
        
        # Store the time now
        now = time.time()
        if self.last_run is None:
            return True  # if hasnt run, run now
        if self.next_run <= now:
            return True
        return False


    def determine_next_run(self) -> float:
        """ calculate next_run value """    
        # triggers every xx seconds
        # if hasnt run, run now
        if self.last_run is None:
            next_run = time.time()
        else:
            next_run = self.last_run + self.seconds
        return next_run
