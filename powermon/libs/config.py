""" config.py """
from copy import deepcopy

def safe_config(config):
    """return a config dict that hides passwords etc"""
    keys_to_hide = ['password', 'victron_key']
    if not isinstance(config, dict):
        return config
    _config = deepcopy(config)
    for key in _config.keys():
        if isinstance(_config[key], dict):
            _config[key] = safe_config(_config[key])
        if key in keys_to_hide:
            _config[key] = "******"
    return _config

class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
