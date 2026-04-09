from datetime import datetime
class Loop():
    """ loop object to abstract looping functions """

    @classmethod
    def from_config(cls, loop_config):
        _loop = cls(delay=loop_config)
        return _loop

    def __str__(self):
        return f"{self.__class__.__name__}: {self.run_once=}, {self.delay=}, {self.loop_runs}, {self.last_run=}"

    def __init__(self, delay=None):
        self.run_once = False
        self.last_run = None
        self.loop_runs = 0
        self.delay = delay

    def _touch(self):
        self.last_run = datetime.now()
        self.loop_runs += 1

    @property
    def delay(self):
        if self._delay is None:
            return 0
        return self._delay

    @delay.setter
    def delay(self, value):
        try:
            self._delay = int(value)
        except (TypeError, ValueError):
            self.run_once = True
            self._delay = None


    def should_loop(self):
        if all([self.run_once, self.last_run is not None]):
            # this is a run once 'loop', that has already run once
            return False
        self._touch()
        return True
            

    #    try:
    #         if loop is None:
    #             loop = False
    #         else:
    #             loop = float(loop) + 0.01  # adding a little bit so is delay is 0, loop != False
    #     
    #     log.debug("loop set to: %s", loop)