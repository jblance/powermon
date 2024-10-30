""" outputs / abstractoutput.py """
import logging
from abc import ABC, abstractmethod

from pydantic import BaseModel

from powermon.commands.result import Result
from powermon.outputformats.abstractformat import AbstractFormat, AbstractFormatDTO

log = logging.getLogger("Output")


class AbstractOutputDTO(BaseModel):
    """ data transfer model for AbstractOutput class """
    output_type: str
    topic: None | str
    formatter: AbstractFormatDTO


class AbstractOutput(ABC):
    """ base class for all output modules """
    def __init__(self, name=None) -> None:
        self.name = name
        # self.command_code : str = "not_set"
        # self.device_id : str = "not_set"
        self.topic = None  # TODO: check why topic is needed here

    def to_dto(self) -> AbstractOutputDTO:
        """ convert output object to a data transfer object """
        if self.formatter is None:
            format_dto = "None"
        else:
            format_dto = self.formatter.to_dto()
        return AbstractOutputDTO(output_type=self.name, topic=self.topic, formatter=format_dto)

    @property
    def formatter(self):
        """ the formatter for this output """
        return getattr(self, "_formatter", None)

    @formatter.setter
    def formatter(self, formatter : AbstractFormat):
        self._formatter = formatter

    @abstractmethod
    def process(self, command=None, result: Result = None, mqtt_broker=None, device_info=None):
        """ entry point of any output class """
        raise NotImplementedError("need to implement process function")
