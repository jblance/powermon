""" powermon / outputformats / bmsresponse.py """
import logging
from powermon.outputformats.abstractformat import AbstractFormat, AbstractFormatDTO
from powermon.commands.result import Result
from powermon.commands.reading import Reading
from powermon.libs.errors import ConfigError

log = logging.getLogger("bmsresponse")


class BMSResponse(AbstractFormat):
    """ bmsresponse in PI30 format """
    def __init__(self, config):
        super().__init__(config)
        self.name = "bmsresponse"

        # response type
        self.response_protocol = config.get("protocol", "not-configured")

        # values from BMS
        self.data = {'battery_voltage': None, 'battery_soc': None, 'discharge_on': None, 'charge_on': None}
        # config set values
        self.data['force_charge'] = config.get("", False)
        self.data['battery_charge_voltage'] = config.get("battery_charge_voltage")
        self.data['battery_float_voltage'] = config.get("battery_float_voltage")
        self.data['battery_cutoff_voltage'] = config.get("battery_cutoff_voltage")
        self.data['battery_max_charge_current'] = config.get("battery_max_charge_current")
        self.data['battery_max_discharge_current'] = config.get("battery_max_discharge_current")
        # todos
        self.data['battery_connected'] = True

    def __str__(self):
        return f"{self.name}: generates the BMSResponse for a PI30 inverter"

    def format(self, command, result: Result, device_info) -> list:

        _result = []

        # check for error in result
        if result.error:
            return _result

        if len(result.readings) == 0:
            return _result

        display_data : list[Reading] = self.format_and_filter_data(result)
        # print(display_data)

        # build data to display
        for reading in display_data:
            name = self.format_key(reading.data_name)
            value = reading.data_value
            # unit = reading.data_unit
            match name:
                case 'battery_voltage':
                    self.data['battery_voltage'] = value
                case 'battery_state_of_charge':
                    self.data['battery_soc'] = value
                case 'discharge_mos_on':
                    self.data['discharge_on'] = value
                case 'charge_mos_on':
                    self.data['charge_on'] = value
                case 'battery_undervoltage_protection_setting':
                    self.data['battery_cutoff_voltage'] = value
                case 'charge_current_protection_setting':
                    self.data['battery_max_charge_current'] = value
                case 'discharge_current_protection_setting':
                    self.data['battery_max_discharge_current'] = value

        # print(self.data)
        # result.append(self.data)
        match self.response_protocol:
            case "PI30" | "pi30":
                # check for required items (either in config or response)
                for item in ('battery_charge_voltage', 'battery_float_voltage', 'battery_cutoff_voltage', 'battery_max_charge_current', 'battery_max_discharge_current'):
                    if not self.data[item]:
                        raise ConfigError(f"'{item}' not defined in config for bmsresponse output format and not in BMS response data")
                _response = (f"BMS{not self.data['battery_connected']:01d} {self.data['battery_soc']:03d} {self.data['force_charge']:0d} "
                    f"{not self.data['discharge_on']:01d} {not self.data['charge_on']:01d} "
                    f"{int(self.data['battery_charge_voltage'] * 10):03d} {int(self.data['battery_float_voltage'] * 10):03d} {int(self.data['battery_cutoff_voltage'] * 10):03d} "
                    f"{int(self.data['battery_max_charge_current'] * 10):04d} {int(self.data['battery_max_discharge_current'] * 10):04d}")
            case "not-configured":
                raise ConfigError("'protocol' not defined in config for bmsresponse output format")
            case _:
                raise ConfigError(f"unknown response protocol ({self.response_protocol}) for BMS response")
        _result.append(_response)
        return _result

    @classmethod
    def from_dto(cls, dto: AbstractFormatDTO):
        """ build class object from dto """
        return cls(config=dto)
