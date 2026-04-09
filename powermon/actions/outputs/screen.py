""" outputs / screen.py """
import logging

from powermon.commands.result import Result
from .output import Output

log = logging.getLogger("screen")


class Screen(Output):
    """outputs the results to the screen as per the formatter supplied """
    def __init__(self, formatter = None):
        super().__init__(name="Screen")
        self.formatter = formatter

    def __str__(self):
        return f"{self.__class__}: outputs the results to the screen as per the formatter supplied"

    def __repr__(self):
        return f"Screen(formatter={self.formatter!r})"

    def process(self, command=None, result: Result = None, device=None):
        log.info("Using output sender: screen")
        log.debug("formatter: %s, result: %s, device: %s", self.formatter, result, device)

        if self.formatter is None:
            print("Configured formatter not found or invalid")
            return

        formatted_data = self.formatter.format(command=command, result=result, device=device)
        if formatted_data is None:
            print("Nothing returned from data formatting")
            return

        for line in formatted_data:
            print(line)

        if result.error:
            print("Errors occurred during processing")
            for error in result.error_messages:
                print(error)

    @classmethod
    def from_config(cls, output_config) -> "Screen":
        """If we need to include any config for the Screen output but the processing here"""
        log.debug("config: %s", output_config)
        return cls()
