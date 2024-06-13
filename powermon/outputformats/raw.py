""" powermon / outputformats / raw.py """
import logging
from powermon.outputformats.abstractformat import AbstractFormat
from powermon.commands.result import Result

log = logging.getLogger("raw")


class Raw(AbstractFormat):
    """ return the raw response """
    def __init__(self, config):
        super().__init__(config)
        self.name = "raw"

    def format(self, command, result: Result, device_info):
        log.info("Using output formatter: %s", self.name)

        data = result.raw_response
        log.debug("raw formatter data: %s", data)
        return [data]
