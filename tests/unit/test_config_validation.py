""" test_config_validation.py """
import unittest
from glob import glob

from pydantic import ValidationError

from powermon.powermon import _read_yaml_file
from powermon.config.powermon_config import PowermonConfig


class TestConfigModel(unittest.TestCase):
    """Test that all the configuration files in the powermon/config directory can be validated by the ConfigModel class"""
    def test_validate_config_files(self):
        """ validate all the yaml config files """
        files = glob('docker/*.yaml')
        files.extend(glob('docker/dev/config/*.yaml'))
        files.extend(glob('tests/config/*.yaml'))
        for filename in files:
            # print(f"Checking valid: {filename}")
            config = _read_yaml_file(filename)
            config_model = PowermonConfig(**config)
            self.assertTrue(config_model is not None)
            self.assertIsInstance(config_model, PowermonConfig)

    def test_invalid_config_files(self):
        """ test that invalid config file raise exception """
        files = glob('tests/config_errors/*.yaml')
        for filename in files:
            # print(f"Checking invalid: {filename}")
            config = _read_yaml_file(filename)
            # config_model = ConfigModel(config=config)
            with self.assertRaises(ValidationError):
                PowermonConfig(**config)
