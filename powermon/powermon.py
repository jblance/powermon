# !/usr/bin/python3
"""main powermon code"""
import asyncio
import json
import logging
import time
from argparse import ArgumentParser
from logging import Logger
from platform import python_version

import yaml                             # ty: ignore[unresolved-import]
from pyaml_env import parse_config      # ty: ignore[unresolved-import]
from pydantic import ValidationError    # ty: ignore[unresolved-import]
# from rich import print as rprint        # ty: ignore[unresolved-import]

from . import _, __version__
from ._config import PowermonConfig
from .daemons import Daemon
from .devices import Device
from .instructions import Instruction
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
            # with open(yaml_file, "r", encoding="utf-8") as stream:
            #     _yaml = yaml.safe_load(stream)
            _yaml = parse_config(yaml_file)
        except yaml.YAMLError as exc:
            raise yaml.YAMLError(f"Error processing yaml file: {exc}") from exc
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Error opening yaml file: {exc}") from exc
    return _yaml


def _process_command_line_overrides(args):
    """override config with command line options"""
    _config = {}
    if args.config:
        _config = json.loads(args.config)
    if args.once:
        _config["loop"] = "once"
    if args.info:
        _config["debuglevel"] = logging.INFO
    if args.debug:
        _config["debuglevel"] = logging.DEBUG
    return _config


def main():
    """entry point for powermon command"""
    asyncio.run(async_main())

async def async_main():
    """powermon command function"""
    _name: str = _("Power Device Monitoring Utility")
    description: str = f"{_name}, version: {__version__}, python version: {python_version()}"  # pylint: disable=C0301
    parser: ArgumentParser = ArgumentParser(description=description)

    parser.add_argument(
        "-C",
        "--configFile",
        nargs="?",
        type=str,
        help=_("Full location of config file (defaults to ./powermon.yaml)"),
        const="./powermon.yaml",
        default=None,
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="""Supply config items on the commandline in json format, \
             eg '{"device": {"port":{"type":"test"}}, "commands": [{"command":"QPI"}]}'""",
    )
    parser.add_argument("-V", "--validate", action="store_true", help=_("Validate the configuration"))
    parser.add_argument("-v", "--version", action="store_true", help=_("Display the version"))
    parser.add_argument("-1", "--once", action="store_true", help=_("Only loop through config once"))
    parser.add_argument("--force", action="store_true", help=_("Force commands to run even if wouldnt be triggered (should only be used with --once)"))
    parser.add_argument("-I", "--info", action="store_true", help=_("Enable Info and above level messages"))
    parser.add_argument("-D", "--debug", action="store_true", help=_("Enable Debug and above (i.e. all) messages"))
    parser.add_argument("-a", "--adhoc", type=str, metavar='COMMAND', default=None, help=_("Send adhoc command to mqtt adhoc command queue - needs config file specified and populated"))

    args = parser.parse_args()
    # prog_name = parser.prog

    # Temporarily set debug level based on command line options
    log.setLevel(logging.WARNING)
    if args.info:
        log.setLevel(logging.INFO)
    if args.debug:
        log.setLevel(logging.DEBUG)

    # Display version if asked
    log.info(description)
    if args.version:
        print(description)
        return None

    # Build configuration from config file and command line overrides
    log.info("Using config file: %s", args.configFile)
    # build config with details from config file - including env variable expansion
    _config = _read_yaml_file(args.configFile)

    # build config - override with any command line arguments
    _config.update(_process_command_line_overrides(args))

    # validate config
    try:
        powermon_config: PowermonConfig = PowermonConfig(**_config) # ty: ignore[missing-argument]
        log.debug(powermon_config)
        log.info("Config validation successful")
    except ValidationError as exception:
        # if config fails to validate, print reason and exit
        print(_("Config validation failed"))
        print(f"{_config=}")
        print(exception)
        return None

    if args.validate:
        # if --validate option set, only do validation
        print(_("Config validation successful"))
        return None

    # set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    log.setLevel(powermon_config.debuglevel)

    # build mqtt broker object
    # mqtt_broker = MqttBroker.from_config(config=powermon_config.mqttbroker)
    mqtt_broker: MqttBroker = MqttBroker.from_config(powermon_config.mqttbroker)
    log.info(mqtt_broker)

    # build the daemon object
    daemon: Daemon = Daemon.from_config(config=powermon_config.daemon)
    log.info(daemon)

    # build device object(s)
    devices: list[Device] = []
    for device_config in powermon_config.devices:
        # build the device object from the config
        _device: Device = await Device.from_config(device_config)
        # add reference to mqtt broker
        _device.mqtt_broker = mqtt_broker

         # add instructions to device instruction list
        for instruction_config in device_config.instructions:
            log.info("Adding instruction, config: %s", instruction_config)
            # print('instruction_config', instruction_config)
            _device.add_instruction(Instruction.from_config(instruction_config))

        # add to devices list
        log.info(_device)
        devices.append(_device)

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
                await device.run_instructions(args.force)

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
