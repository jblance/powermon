# !/usr/bin/python3
"""main powermon code"""
import asyncio
import json
import logging
import time
from argparse import ArgumentParser
from copy import deepcopy
from platform import python_version

import yaml
from pyaml_env import parse_config
from pydantic import ValidationError

from powermon.commands.command import Command
from powermon.device import Device
from powermon.libs.apicoordinator import ApiCoordinator
from powermon.configmodel.config_model import ConfigModel
from powermon.libs.daemon import Daemon
from powermon.libs.mqttbroker import MqttBroker
from powermon.libs.version import __version__  # noqa: F401
from powermon.protocols import list_protocols

# Set-up logger
log = logging.getLogger("")
FORMAT = "%(asctime)-15s:%(levelname)s:%(module)s:%(funcName)s@%(lineno)d: %(message)s"
logging.basicConfig(format=FORMAT)


def _run_async(coroutine):
    try:
        async_loop = asyncio.get_running_loop()
    except RuntimeError:
        async_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(async_loop)
    return async_loop.run_until_complete(coroutine)


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

def _safe_config(config):
    """return a config dict that hides passwords etc"""
    keys_to_hide = ['password', 'victron_key']
    _config = deepcopy(config)
    for key in _config.keys():
        if isinstance(_config[key], dict):
            _config[key] = _safe_config(_config[key])
        if key in keys_to_hide:
            _config[key] = "******"
    return _config



def main():
    """main entry point for powermon command"""
    description = f"Power Device Monitoring Utility, version: {__version__}, python version: {python_version()}"  # pylint: disable=C0301
    parser = ArgumentParser(description=description)

    parser.add_argument(
        "-C",
        "--configFile",
        nargs="?",
        type=str,
        help="Full location of config file",
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
    parser.add_argument("-V", "--validate", action="store_true", help="Validate the configuration")
    parser.add_argument("-v", "--version", action="store_true", help="Display the version")
    parser.add_argument("--listProtocols", action="store_true", help="Display the currently supported protocols")
    parser.add_argument("-1", "--once", action="store_true", help="Only loop through config once")
    parser.add_argument("--force", action="store_true", help="Force commands to run even if wouldnt be triggered (should only be used with --once)")
    parser.add_argument("-D", "--debug", action="store_true", help="Enable Debug and above (i.e. all) messages")
    parser.add_argument("-I", "--info", action="store_true", help="Enable Info and above level messages")
    parser.add_argument("--adhoc", type=str, default=None, help="Send adhoc command to mqtt adhoc command queue - needs config file specified and populated")

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

    # Do enquiry commands
    # - List Protocols
    if args.listProtocols:
        list_protocols()
        return None

    # Build configuration from config file and command line overrides
    log.info("Using config file: %s", args.configFile)
    # build config with details from config file
    config = _read_yaml_file(args.configFile)

    # build config - override with any command line arguments
    config.update(_process_command_line_overrides(args))

    # validate config
    try:
        config_model = ConfigModel(config=config)
        log.debug(config_model)
        log.info("Config validation successful")
        if args.validate:
            # if --validate option set, only do validation
            print("Config validation successful")
            return None
    except ValidationError as exception:
        # if config fails to validate, print reason and exit
        print("Config validation failed")
        print(f"{config=}")
        print(exception)
        return None

    # logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    log.setLevel(config.get("debuglevel", logging.WARNING))

    # debug config
    log.info("config: %s", _safe_config(config))  # TODO: fix dumping of password and victron_key

    # build mqtt broker object (optional)
    mqtt_broker = MqttBroker.from_config(config=config.get("mqttbroker"))
    log.info(mqtt_broker)

    # build device object (required)
    device = Device.from_config(config=config.get("device"))
    device.mqtt_broker = mqtt_broker
    log.debug(device)

    # process adhoc command line command
    if args.adhoc:
        print("Received an adhoc command")
        # if not running mqttbroker, run command directly
        if device.mqtt_broker.disabled or not device.mqtt_broker.is_connected:
            print("Running adhoc command to non-connected device")
            adhoc_command_config = {"command": args.adhoc}
            device.add_command(Command.from_config(adhoc_command_config))
            _run_async(device.initialize())
            _run_async(device.run(True))
            _run_async(device.finalize())
            return
        # post adhoc command to mqtt
        device.mqtt_broker.post_adhoc_command(command_code=args.adhoc)
        # _command = Command.from_code(args.adhoc)
        # _command.command_definition = device.port.protocol.get_command_definition(args.adhoc)
        # print(_command)
        return
    # add commands to device command list
    for command_config in config.get("commands"):
        log.info("Adding command, config: %s", command_config)
        device.add_command(Command.from_config(command_config))
    log.info(device)

    # build the daemon object (optional)
    daemon = Daemon.from_config(config=config.get("daemon"))
    log.info(daemon)

    # build api coordinator
    api_coordinator = ApiCoordinator.from_config(config=config.get("api"))
    api_coordinator.set_device(device)
    api_coordinator.set_mqtt_broker(mqtt_broker)
    log.info(api_coordinator)

    # initialize api coordinator
    api_coordinator.initialize()

    # initialize daemon
    daemon.initialize()
    api_coordinator.announce(daemon)

    # initialize device
    _run_async(device.initialize())
    api_coordinator.announce(device)

    # loop config
    loop = config.get("loop", "once")
    if loop == "once":
        loop = False
    else:
        loop = int(loop)
    log.debug("loop set to: %s", loop)

    # Main working loop
    try:
        while True:
            # tell the daemon we're still working
            daemon.watchdog()

            # run device loop (ie run any needed commands)
            _run_async(device.run(args.force))

            # run api coordinator ...
            api_coordinator.run()

            # only run loop once if required
            if not loop:
                break

            # add small delay in loop
            time.sleep(loop)

    except KeyboardInterrupt:
        print("KeyboardInterrupt - stopping")
    finally:
        # disconnect device
        _run_async(device.finalize())

        # disconnect mqtt
        mqtt_broker.stop()

        # stop the daemon
        daemon.stop()
