from powermon.config import PowermonConfig
from powermon.domain import DeviceConfig, TaskConfig
from powermon.ports import MockPortConfig


def generate_base_config() -> PowermonConfig:
    """
    Generate a minimal, valid PowermonConfig using model defaults.
    No user interaction yet.
    """

    base_task = TaskConfig(
        command="QID",  # safe, informational default
    )

    base_device = DeviceConfig(
        name="example_device",
        port=MockPortConfig(),
        tasks=[base_task],
    )

    return PowermonConfig(
        devices=[base_device],
    )