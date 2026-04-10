from . import Trigger

class TriggerDisabled(Trigger):

    def __str__(self):
        return f"{self.__class__.__name__}"


    def __init__(self):
        pass

    def is_due(self) -> bool:
        """ determine if this trigger is due or not """
        return False