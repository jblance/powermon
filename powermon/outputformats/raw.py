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

    def __str__(self):
        return f"{self.name}: outputs the response as received from the device"

    def get_options(self):
        """ return a dict of all options and defaults """
        return {}

    def format(self, command, result: Result, device_info):
        log.info("Using output formatter: %s", self.name)

        data = result.raw_response
        log.debug("raw formatter data: %s", data)
        return [data]
