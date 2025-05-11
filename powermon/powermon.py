# !/usr/bin/python3
"""main powermon code"""
import asyncio
# import gettext
import json
import logging
# import pathlib
import time
from argparse import ArgumentParser
from platform import python_version

import yaml
from pyaml_env import parse_config
from pydantic import ValidationError

from powermon import MqttBroker, _, __version__

from .commands.command import Command
from .config.powermon_config import PowermonConfig
from .device import Device
from .libs.apicoordinator import ApiCoordinator
from .daemons import from_config as daemon_from_config
#from powermon.libs.mqttbroker import MqttBroker
# from powermon.libs.version import __version__  # noqa: F401
from .protocols import from_device_config as protocols_from_device_config
from .protocols import list_commands, list_protocols
from .ports import from_config as port_from_config

# Set-up logger
log = logging.getLogger("")
FORMAT = "%(asctime)-15s:%(levelname)s:%(module)s:%(funcName)s@%(lineno)d: %(message)s"
logging.basicConfig(format=FORMAT)


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
    _name = _("Power Device Monitoring Utility")
    description = f"{_name}, version: {__version__}, python version: {python_version()}"  # pylint: disable=C0301
    parser = ArgumentParser(description=description)

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
    parser.add_argument("-V", "--validate", action="store_true", help="Validate the configuration")
    parser.add_argument("-v", "--version", action="store_true", help="Display the version")
    parser.add_argument("--listProtocols", action="store_true", help="Display the currently supported protocols")
    parser.add_argument("--listCommands", type=str, metavar='PROTOCOL', default=None, help="Display available commands for PROTOCOL")
    parser.add_argument("-1", "--once", action="store_true", help="Only loop through config once")
    parser.add_argument("--force", action="store_true", help="Force commands to run even if wouldnt be triggered (should only be used with --once)")
    parser.add_argument("-I", "--info", action="store_true", help="Enable Info and above level messages")
    parser.add_argument("-D", "--debug", action="store_true", help="Enable Debug and above (i.e. all) messages")
    parser.add_argument("-a", "--adhoc", type=str, metavar='COMMAND', default=None, help="Send adhoc command to mqtt adhoc command queue - needs config file specified and populated")

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
        print(description)
        list_protocols()
        return None

    # - List Commands
    if args.listCommands:
        print(description)
        list_commands(name=args.listCommands)
        return None

    # Build configuration from config file and command line overrides
    log.info("Using config file: %s", args.configFile)
    # build config with details from config file - including env variable expansion
    _config = _read_yaml_file(args.configFile)

    # build config - override with any command line arguments
    _config.update(_process_command_line_overrides(args))

    # validate config
    try:
        powermon_config = PowermonConfig(**_config)
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
    mqtt_broker = MqttBroker(powermon_config.mqttbroker)
    log.info(mqtt_broker)

    # build the daemon object (optional)
    daemon = daemon_from_config(config=powermon_config.daemon)
    log.info(daemon)

    # build api coordinator
    api_coordinator = ApiCoordinator.from_config(config=powermon_config.api)
    log.info(api_coordinator)

    # build device object (required)
    device = Device(powermon_config)
    ## get the protocol 
    _protocol = protocols_from_device_config(config=powermon_config.device)
    device.port = await port_from_config(config=powermon_config.device.port, protocol=_protocol, serial_number=powermon_config.device.serial_number)
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
            await device.initialize()
            await device.run(True)
            await device.finalize()
            return
        # post adhoc command to mqtt
        device.mqtt_broker.post_adhoc_command(command_code=args.adhoc)
        # _command = Command.from_code(args.adhoc)
        # _command.command_definition = device.port.protocol.get_command_definition(args.adhoc)
        # print(_command)
        return
    # add commands to device command list
    for command_config in powermon_config.commands:
        log.info("Adding command, config: %s", command_config)
        device.add_command(Command.from_config(command_config))
    log.info(device)

    
    

    # initialize api coordinator
    api_coordinator.set_device(device)
    api_coordinator.set_mqtt_broker(mqtt_broker)
    
    api_coordinator.initialize()

    # initialize daemon
    daemon.initialize()
    api_coordinator.announce(daemon)

    # initialize device
    await device.initialize()
    api_coordinator.announce(device)

    # loop config
    loop = powermon_config.loop
    try:
        if loop is None:
            loop = False
        else:
            loop = float(loop) + 0.01  # adding a little bit so is delay is 0, loop != False
    except ValueError:
        log.warning("loop unable to cast %s to float - defaulting to 'False'", loop)
        loop = False
    log.debug("loop set to: %s", loop)

    # Main working loop
    try:
        while True:
            # tell the daemon we're still working
            daemon.watchdog()

            # run device loop (ie run any needed commands)
            await device.run(args.force)

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
        await device.finalize()

        # disconnect mqtt
        mqtt_broker.stop()

        # stop the daemon
        daemon.stop()
