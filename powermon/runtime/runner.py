import asyncio
import time
import logging
from typing import List, Optional

from powermon.daemons import Daemon
from powermon.devices import Device
from powermon.mqttbroker import MqttBroker

log = logging.getLogger(__name__)

MIN_SLEEP_SECONDS = 0.2
MAX_SLEEP_SECONDS = 5.0


class RuntimeState:
    def __init__(self) -> None:
        self.running = True

    def stop(self) -> None:
        self.running = False


async def run_worker(
    config,
    *,
    once: bool = False,
    force_tasks: bool = False,
) -> None:
    """
    Main runtime worker.

    - Runs continuously by default
    - Scheduling is entirely action-based
    - No global loop or cadence
    """

    state = RuntimeState()

    mqtt_broker = MqttBroker.from_config(config.mqttbroker)
    daemon = Daemon.from_config(config=config.daemon)

    devices: List[Device] = await Device.from_configs(
        config.devices,
        mqtt_broker=mqtt_broker,
    )

    daemon.initialize()
    for device in devices:
        await device.initialize()

    try:
        while state.running:
            daemon.watchdog()
            now = time.time()

            # Run due actions
            for device in devices:
                await device.run_due_tasks(
                    now=now,
                    force=force_tasks,
                )

            if once:
                break

            # Determine next due task time
            next_due: Optional[float] = None
            for device in devices:
                ts = device.next_due_timestamp(now=now)
                if ts is not None:
                    next_due = ts if next_due is None else min(next_due, ts)

            if next_due is None:
                sleep_for = MAX_SLEEP_SECONDS
            else:
                sleep_for = max(
                    MIN_SLEEP_SECONDS,
                    min(MAX_SLEEP_SECONDS, next_due - now),
                )

            await asyncio.sleep(sleep_for)

    finally:
        log.info("Shutting down runtime")

        for device in devices:
            await device.finalize()

        mqtt_broker.stop()
        daemon.stop()