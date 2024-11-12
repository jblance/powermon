""" powermon / outputformats / json_fmt.py """
import json
import logging
from powermon.outputformats.abstractformat import AbstractFormat, AbstractFormatDTO
from powermon.commands.result import Result
from powermon.commands.reading import Reading

log = logging.getLogger("json")


class Json(AbstractFormat):
    """ simple format - {name}={value}{unit} format """
    def __init__(self, config):
        super().__init__(config)
        self.name = "json"
        self.json_format = config.get("format", "basic")
        self.include_missing = config.get("include_missing", False)

    # def set_command_description(self, command_description):
    #     pass
    def __str__(self):
        return f"{self.name}: generates json representation of the results"

    def get_options(self):
        """ return a dict of all options and defaults """
        extra_options = {"format": "basic", "include_missing": False}
        options = super().get_options()
        options.update(extra_options)
        return options

    def format(self, command=None, result: Result=None, device_info=None) -> list:

        _result = []

        if result is None:
            return _result
        # if jsonpickle is None:
        #     return _result

        # check for error in result
        if result.error:
            _result.append(f"Error Count: {len(result.error_messages)}")
            for i, message in enumerate(result.error_messages):
                _result.append(f"Error #{i}: {message}")
            # return _result

        if len(result.readings) == 0:
            return _result

        display_data : list[Reading] = self.format_and_filter_data(result)

        # build data to display
        for reading in display_data:
            # match self.json_format:
            #     case 'basic':  # only basic format type so far
            pickle = {'data_name': self.format_key(reading.data_name)}
            wanted_items = ['data_value', 'data_unit']
            if self.extra_info:
                wanted_items.extend(['icon', 'state_class', 'device_class'])

            if self.include_missing:
                pickle.update({key: getattr(reading, key) for key in wanted_items})
            else:
                pickle.update({key: getattr(reading, key) for key in wanted_items if getattr(reading, key) is not None})
            _result.append(json.dumps(pickle))
        return _result

    @classmethod
    def from_dto(cls, dto: AbstractFormatDTO):
        """ build class object from dto """
        return cls(config=dto)
