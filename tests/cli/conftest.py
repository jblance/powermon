import pytest  # ty: ignore[unresolved-import]
from rich.console import Console  # ty: ignore[unresolved-import]

@pytest.fixture
def console():
    return Console(
        force_terminal=True,
        color_system="truecolor",
        width=120,
        record=True,
    )
