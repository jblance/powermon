"""cli.py - hold classes for the powermon cli"""
import logging
from argparse import ArgumentParser
from platform import python_version

from powermon.libs.version import __version__  # noqa: F401

# Set-up logger
log = logging.getLogger("")
FORMAT = "%(asctime)-15s:%(levelname)s:%(module)s:%(funcName)s@%(lineno)d: %(message)s"
logging.basicConfig(format=FORMAT)


def main():
    """main entry point for the powermon cli
    """
    description = f"Power Device Monitoring Utility CLI, version: {__version__}, python version: {python_version()}"  # pylint: disable=C0301
    parser = ArgumentParser(description=description)

    parser.add_argument("-v", "--version", action="store_true", help="Display the version")
    parser.add_argument("--bleScan", action="store_true", help="Scan for BLW devices")

    args = parser.parse_args()

    # Display version if asked
    log.info(description)
    if args.version:
        print(description)
        return None

    if args.bleScan:
        import asyncio
        from bleak import BleakScanner


        async def scan_function():
            devices = await BleakScanner.discover()
            for d in devices:
                print(d)


        asyncio.run(scan_function())
