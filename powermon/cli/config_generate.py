from powermon._config import PowermonConfig
from powermon.devices import DeviceConfig
from powermon.actions import ActionConfig
from powermon.devices.ports import TestPortConfig


def generate_base_config() -> PowermonConfig:
    """
    Generate a minimal, valid PowermonConfig using model defaults.
    No user interaction yet.
    """

    base_action = ActionConfig(
        command="QID",  # safe, informational default
    )

    base_device = DeviceConfig(
        name="example_device",
        port=TestPortConfig(),
        actions=[base_action],
    )

    return PowermonConfig(
        devices=[base_device],
    )