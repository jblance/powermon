# !/usr/bin/python3
from argparse import ArgumentParser
import logging

from .version import __version__  # noqa: F401

log = logging.getLogger('powermon')
# setup logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
# set default log levels
log.setLevel(logging.WARNING)
logging.basicConfig()


def main():
    parser = ArgumentParser(description='Power Monitor Utility, version: {}'.format(__version__))
    args = parser.parse_args()

    print('Powermon version {}'.format(__version__))
    print(args)
