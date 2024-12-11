""" powermon / outputformats / cache.py """
import logging
from time import time

from powermon.outputformats.abstractformat import AbstractFormat, AbstractFormatDTO
from powermon.commands.result import Result
from powermon.commands.reading import Reading

log = logging.getLogger("Cache")


class Cache(AbstractFormat):
    """ simple format - {name}={value}{unit} format """
    def __init__(self, config):
        super().__init__(config)
        self.name = "cache"


    def __str__(self):
        return f"{self.name}: generates mqtt messages suited to populating the results cache"


    def format(self, command, result: Result, device_info) -> list:
        ## cache format
        #
        # topic: powermon/device-by-name/{device_name}/{category}/{parameter_name}
        # {category}: 
        #           config:   device_info and port details from config file
        #           info:     informational data from inverter (fixed), eg QID, QVFW, QPI etc
        #           settings: inverter settings, eg QPIRI etc
        #           defaults: setting default info from inverter, eg QDI
        #           data:     data values from inverter(changeable)
        #           errors:   separate topic for (application) errors
        #
        # payload: json with minimum of {'value': 123, 'measurement_time': 'some-date-value'}

        # result should be a list of dict of format {'topic': <topic>, 'payload': <json payload>}
        _result = []

        device_name = device_info.name.replace(' ', '_')
        category = command.command_definition.category
        topic_prefix = f"powermon/device-by-name/{device_name}/{category}"
        # print(topic_prefix)

        # check for error in result
        # TODO: update for errors
        if result.error:
            error_topic_prefix = f"powermon/device-by-name/{device_name}/errors"
            topic = f"{error_topic_prefix}/Error_Count"
            payload = {}
            payload['value'] = len(result.error_messages)
            payload['measurement_time'] = time()
            _result.append({'topic': topic, 'payload': payload})

            for i, message in enumerate(result.error_messages):
                topic = f"{error_topic_prefix}/Error_#{i}"
                _result.append(f"Error #{i}: {message}")
                payload['value'] = {message}
                payload['measurement_time'] = time()
                _result.append({'topic': topic, 'payload': payload})

        if len(result.readings) == 0:
            return _result

        display_data : list[Reading] = self.format_and_filter_data(result)

        # build data to display
        for reading in display_data:
            parameter_name = self.format_key(reading.data_name)
            topic = f"{topic_prefix}/{parameter_name}"
            payload = {}
            payload['value'] = reading.data_value
            payload['measurement_time'] = time()
            if reading.data_unit:
                payload['unit'] = reading.data_unit
            if reading.device_class:
                payload['device_class'] = reading.device_class
            if reading.icon:
                payload['icon'] = reading.icon
            if reading.state_class:
                payload['state_class'] = reading.state_class
            _result.append({'topic': topic, 'payload': payload})
        return _result

    @classmethod
    def from_dto(cls, dto: AbstractFormatDTO):
        """ build class object from dto """
        return cls(config=dto)
