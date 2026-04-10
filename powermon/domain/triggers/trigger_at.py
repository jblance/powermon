import datetime
import time

from . import Trigger


class TriggerAt(Trigger):

    def __str__(self):
        return f"{self.__class__.__name__}: {self.run_at=}, last_run={self.get_last_run()}, next_run={self.get_next_run()}"


    def __init__(self, at):
        self.run_at = at
        self.last_run : float | None = None
        self.next_run : float = self.determine_next_run()

    def is_due(self) -> bool:
        """ determine if this trigger is due or not """
        # Store the time now
        now = time.time()

        if self.next_run is None:
            #log.warning("at type trigger failed to set next run for %s" % command)
            return False
        if self.next_run <= now:
            return True
        return False

    def determine_next_run(self) -> float:
        """ calculate next_run value """
        # triggers at specific time each day
        dt_today = datetime.datetime.now()
        dt_now = dt_today.time()
        at_time = datetime.time.fromisoformat(self.run_at)
        if dt_now < at_time:
            # needs to run today at at_time
            next_run = dt_today.replace(hour=at_time.hour, minute=at_time.minute, second=at_time.second, microsecond=0).timestamp()
        else:
            # needs to run tomorrow at at_time
            next_run = (dt_today.replace(hour=at_time.hour, minute=at_time.minute, second=at_time.second, microsecond=0) + datetime.timedelta(days=1)).timestamp()
        return next_run
