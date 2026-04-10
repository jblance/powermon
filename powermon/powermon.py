# !/usr/bin/python3
"""main powermon code"""
import asyncio
import json
import logging
import time
from argparse import ArgumentParser
from logging import Logger
from platform import python_version
from typing import Optional

import yaml  # ty: ignore[unresolved-import]
from pyaml_env import parse_config  # ty: ignore[unresolved-import]
from pydantic import ValidationError  # ty: ignore[unresolved-import]

from . import tl, __version__
from ._config import PowermonConfig
from .daemons import Daemon
from .devices import Device
from .actions import Action
from .loop import Loop
from .mqttbroker import MqttBroker

# Set-up logger
log: Logger = logging.getLogger("")
logging.basicConfig(format="%(asctime)-15s:%(levelname)s:%(module)s:%(funcName)s@%(lineno)d: %(message)s")


def _read_yaml_file(yaml_file=None):
    """function to read a yaml file and return dict"""
    _yaml = {}
    if yaml_file is not None:
        try:
            _yaml = parse_config(yaml_file)
        except yaml.YAMLError as exc:
            raise yaml.YAMLError(f"Error processing yaml file: {exc}") from exc
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Error opening yaml file: {exc}") from exc
    return _yaml


def _validate_config(config: Optional[dict] = None):
    try:
        powermon_config: PowermonConfig = PowermonConfig(**config)
        log.debug(powermon_config)
        log.info("Config validation successful")
        return powermon_config
    except ValidationError as exception:
        # if config fails to validate, print reason and exit
        print(tl("Config validation failed"))
        print(f"{config=}")
        print(exception)
        exit(1)


def build_config(args = None) -> PowermonConfig:
    """build the powermon config object from command line args and config file"""
    # read config file
    _config = _read_yaml_file(args.configFile)
    log.info("Using config file: %s", args.configFile)
    # validate config
    return _validate_config(config=_config)


def main():
    """entry point for powermon command"""
    asyncio.run(async_main())


async def async_main():
    """powermon command function"""
    _name: str = tl("Power Device Monitoring Utility")
    description: str = f"{_name}, version: {__version__}, python version: {python_version()}"  # pylint: disable=C0301
    parser: ArgumentParser = ArgumentParser(description=description)

    parser.add_argument(
        "-C",
        "--configFile",
        type=str,
        help=tl("Full location of config file (defaults to ./powermon.yaml)"),
        default="./powermon.yaml",)
    parser.add_argument("-v", "--version", action="store_true", help=tl("Display the version"))
    parser.add_argument("-1", "--once", action="store_true", help=tl("Only loop through config once"))
    parser.add_argument("--force", action="store_true", help=tl("Force commands to run even if wouldnt be triggered (should only be used with --once)"))
    parser.add_argument("-I", "--info", action="store_true", help=tl("Enable Info and above level messages"))
    parser.add_argument("-D", "--debug", action="store_true", help=tl("Enable Debug and above (i.e. all) messages"))
    parser.add_argument("-a", "--adhoc", type=str, metavar='COMMAND', default=None, help=tl("Send adhoc command to mqtt adhoc command queue - needs config file specified and populated"))

    args = parser.parse_args()

    # Display version if asked for
    if args.version:
        print(description)
        return None
    
    # set log level
    if args.info:
        log.setLevel(logging.INFO)
    if args.debug:
        log.setLevel(logging.DEBUG)

    # build config object
    powermon_config: PowermonConfig = build_config(args=args)
    
    log.info(description)
    
    # build mqtt broker object
    mqtt_broker: MqttBroker = MqttBroker.from_config(powermon_config.mqttbroker)
    log.info(mqtt_broker)

    # build the daemon object
    daemon: Daemon = Daemon.from_config(config=powermon_config.daemon)
    log.info(daemon)

    # build list of devices
    devices: list[Device] = await Device.from_configs(powermon_config.devices, mqtt_broker=mqtt_broker)
    log.debug(devices)

    # # TODO: sort out how to make this work
    # # process adhoc command line command
    # if args.adhoc:
    #     print("Received an adhoc command")
    #     # if not running mqttbroker, run command directly
    #     if device.mqtt_broker.disabled or not device.mqtt_broker.is_connected:
    #         print("Running adhoc command to non-connected device")
    #         adhoc_command_config = {"command": args.adhoc}
    #         device.add_command(Command.from_config(adhoc_command_config))
    #         await device.initialize()
    #         await device.run(True)
    #         await device.finalize()
    #         return
    #     # post adhoc command to mqtt
    #     device.mqtt_broker.post_adhoc_command(command_code=args.adhoc)
    #     # _command = Command.from_code(args.adhoc)
    #     # _command.command_definition = device.port.protocol.get_command_definition(args.adhoc)
    #     # print(_command)
    #     return
    
    # initialize daemon
    daemon.initialize()

    # initialize devices
    for device in devices:
        await device.initialize()

    # build loop object
    loop = Loop.from_config(powermon_config.loop)
    log.info(loop)

    # Main working loop
    try:
        while loop.should_loop():
            # tell the daemon we're still working
            daemon.watchdog()

            # run device loop (ie run any needed commands)
            for device in devices:
                await device.run_actions(args.force)

            # add small delay in loop
            time.sleep(loop.delay)

    except KeyboardInterrupt:
        print("KeyboardInterrupt - stopping")
    finally:
        # disconnect device
        for device in devices:
            await device.finalize()

        # disconnect mqtt
        mqtt_broker.stop()

        # stop the daemon
        daemon.stop()
