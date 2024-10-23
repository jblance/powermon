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

class Config():
    pass
