# import logging
from time import time

from .daemon import Daemon

# Set-up logger
# log = logging.getLogger("daemon_simple")

class DaemonSimple(Daemon):

    def __init__(self, keepalive):
        super().__init__(keepalive=keepalive)
        self.type = 'simple'


    def initialize(self):
        """ Daemon initialization activities """
        print("initializing daemon")
        self.last_notify = time()

    def watchdog(self):
        elapsed = time() - self.last_notify
        if (elapsed) > self.keepalive:
            self.last_notify = time()
            print(f"Daemon notify at {self.last_notify}")

    def notify(self, status="OK"):
        # Send status
        self.last_notify = time()
        print(f'Daemon notify: {status}')

    def stop(self):
        # Send stopping
        print('Daemon stopping')

    def log(self, message=None):
        # Print log message
        if message is not None:
            print(f'Daemon message: {message}')
