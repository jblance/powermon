from . import Trigger

class TriggerOnce(Trigger):

    def __str__(self):
        return f"{self.__class__.__name__}: {self.has_run=}"


    def __init__(self):
        self.has_run = False

    def is_due(self) -> bool:
        """ determine if this trigger is due or not """
        if not self.has_run:
            self.has_run = True
            return True
        else:
            return False
