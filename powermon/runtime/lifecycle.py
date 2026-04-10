import logging
import signal
import asyncio
from typing import Callable


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.WARNING),
        format="%(asctime)-15s:%(levelname)s:%(module)s:%(funcName)s@%(lineno)d: %(message)s",
    )


def install_signal_handlers(stop_cb: Callable[[], None]) -> None:
    """
    Install SIGINT / SIGTERM handlers that trigger a clean shutdown.
    """

    def _handler(signum, _frame):
        logging.getLogger(__name__).info("Received signal %s, shutting down", signum)
        stop_cb()

    signal.signal(signal.SIGINT, _handler)
    signal.signal(signal.SIGTERM, _handler)