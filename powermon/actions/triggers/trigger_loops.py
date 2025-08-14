from . import Trigger

class TriggerLoops(Trigger):

    def __str__(self):
        return f"{self.__class__.__name__}: {self.loops=} {self.togo=}"


    def __init__(self, loops):
        self.loops = loops
        self.togo = 0


    def is_due(self) -> bool:
        """ determine if this trigger is due or not """
        if self.togo <= 0:
            self.togo = self.loops
            return True
        else:
            self.togo -= 1
            return False

