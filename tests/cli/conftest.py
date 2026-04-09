import pytest
from rich.console import Console

@pytest.fixture
def console():
    return Console(
        force_terminal=True,
        color_system="truecolor",
        width=120,
        record=True,
    )