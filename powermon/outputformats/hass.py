""" powermon / outputformats / hass.py """
import json as js
import logging
from datetime import datetime
from enum import Enum

import construct as cs

from powermon.commands.command import Command
from powermon.commands.reading import Reading
from powermon.commands.result import Result
from powermon.libs.version import __version__  # noqa: F401
from powermon.outputformats.abstractformat import AbstractFormat

log = logging.getLogger("hass")


class Hass(AbstractFormat):
    """ formatter to generate home assistant auto config mqtt messages """
    def __init__(self, config):
        super().__init__(config)
        self.name = "hass"
        self.discovery_prefix = config.get("discovery_prefix", "homeassistant")
        self.entity_id_prefix = config.get("entity_id_prefix", None)

    def __str__(self):
        return f"{self.name}: generates Home Assistant auto config and update mqtt messages"

    def get_options(self):
        """ return a dict of all options and defaults """
        extra_options = {"discovery_prefix": "homeassistant", "entity_id_prefix": None}
        options = super().get_options()
        options.update(extra_options)
        return options

    def format(self, command: Command, result: Result, device_info) -> list:
        log.info("Using output formatter: %s", self.name)

        config_msgs = []
        value_msgs = []

        _result = []
        if result.readings is None:
            return _result
        display_data : list[Reading] = self.format_and_filter_data(result)
        log.debug("displayData: %s", display_data)

        # build data to display
        for response in display_data:
            # Get key data
            data_name = self.format_key(response.data_name)
            value = response.data_value
            unit = response.data_unit
            icon = response.icon
            device_class = response.device_class
            state_class = response.state_class
            component = response.component or 'sensor'

            # Set component type
            if unit == "bool" or value == "enabled" or value == "disabled":
                print(f'updating sensor to binary sensor for {data_name}')
                component = "binary_sensor"
            # else:
            #     component = "sensor"

            # Make value adjustments
            if component == "binary_sensor":
                if value == 0 or value == "0" or value == "disabled":
                    value = "OFF"
                elif value == 1 or value == "1" or value == "enabled":
                    value = "ON"

            # Object ID
            if self.entity_id_prefix is None:
                object_id = f"{data_name}".lower().replace(" ", "_")
                
            else:
                object_id = f"{self.entity_id_prefix}_{data_name}".lower().replace(" ", "_")
                #name = f"{self.entity_id_prefix} {data_name}"
            name = f"{response.data_name}"

            # Home Assistant MQTT Auto Discovery Message
            #
            # Topic
            # <discovery_prefix>/<component>/[<node_id>/]<object_id>/config, eg homeassistant/binary_sensor/garden/config
            topic_base = f"{self.discovery_prefix}/{component}/{object_id}".replace(" ", "_")
            # remove illegal topic characters
            topic_base = topic_base.translate({ord(i): '-' for i in '(){}[]'})
            topic = f"{topic_base}/config"
            state_topic = f"{topic_base}/state"

            # Payload
            # msg '{"name": "garden", "device_class": "motion", "state_topic": "homeassistant/binary_sensor/garden/state", "unit_of_measurement": "°C", "icon": "power-plug"}'
            payload = {
                "name": f"{name}",
                "state_topic": f"{state_topic}",
                "unique_id": f"{object_id}_{device_info.serial_number}",
                # "force_update": "true",
                # "last_reset": str(datetime.now()),
            }

            # Add device info
            # payload["device"] = {"name": f"{device_name}", "identifiers": ["mppsolar"], "model": "PIP6048MAX", "manufacturer": "MPP-Solar"}
            payload["device"] = {
                "name": device_info.name,
                "identifiers": [device_info.serial_number],
                "model": device_info.model,
                "manufacturer": device_info.manufacturer,
            }

            # Add origin info
            payload["origin"] = {
                "name": "powermon",
                "sw_version": __version__,
                "support_url": "https://github.com/jblance/powermon"
            }

            # Add unit of measurement
            if unit and unit != "bool":
                payload["unit_of_measurement"] = f"{unit}"

            # Add icon
            if icon:
                payload.update({"icon": icon})

            # Add device class
            if device_class:
                payload["device_class"] = device_class

            # Add state_class
            if state_class:
                payload["state_class"] = state_class

            # Add options
            if response.definition.options is not None and device_class == "enum":
                if isinstance(response.definition.options, dict):
                    payload["options"] = list(response.definition.options.values())
                else:
                    payload["options"] = response.definition.options

            payloads = js.dumps(payload)
            # print(payloads)
            msg = {"topic": topic, "payload": payloads}
            config_msgs.append(msg)

            # VALUE SETTING
            # convert construct EnumIntegerStrings to a str
            if isinstance(value, cs.EnumIntegerString):
                value = str(value)
            msg = {"topic": state_topic, "payload": value}
            value_msgs.append(msg)

        # order value msgs after config to allow HA time to build entity before state data arrives
        return config_msgs + value_msgs


class HassAutoDiscovery(Hass):
    """ formatter to generate home assistant auto config mqtt messages """
    def __init__(self, config):
        super().__init__(config)
        self.name = "hass_autodiscovery"

    def __str__(self):
        return f"{self.name}: generates Home Assistant auto config (only) mqtt messages"


class HassState(Hass):
    """ formatter to generate home assistant state update mqtt messages """
    def __init__(self, config):
        super().__init__(config)
        self.name = "hass_state"

    def __str__(self):
        return f"{self.name}: generates Home Assistant state update mqtt messages (requires entities to exist or HassAutoDiscovery to have been run first)"
