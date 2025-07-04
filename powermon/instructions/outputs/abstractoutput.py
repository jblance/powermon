""" outputs / abstractoutput.py """
import logging
from abc import ABC, abstractmethod

# from pydantic import BaseModel

from powermon.commands.result import Result
from .formatters.abstractformat import AbstractFormat

log = logging.getLogger("Output")


class AbstractOutput(ABC):
    """ base class for all output modules """
    def __init__(self, name=None) -> None:
        self.name = name
        # self.command_code : str = "not_set"
        # self.device_id : str = "not_set"
        self.topic = None  # TODO: check why topic is needed here


    @property
    def formatter(self):
        """ the formatter for this output """
        return getattr(self, "_formatter", None)


    @formatter.setter
    def formatter(self, formatter : AbstractFormat):
        self._formatter = formatter


    @abstractmethod
    def process(self, command=None, result: Result = None, device=None):
        """ entry point of any output class """
        raise NotImplementedError("need to implement process function")
