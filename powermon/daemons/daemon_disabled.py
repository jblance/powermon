# import logging
from time import time

from .daemon import Daemon

# Set-up logger
# log = logging.getLogger("daemon_simple")

class DaemonDisabled(Daemon):

    def __init__(self, keepalive=60):
        super().__init__(keepalive=keepalive)
        self.type = 'disabled'


    def initialize(self):
        """ Daemon initialization activities """
        self.last_notify = time()

    def watchdog(self):
        elapsed = time() - self.last_notify
        if (elapsed) > self.keepalive:
            self.last_notify = time()

    def notify(self, status="OK"):
        # Send status
        self.last_notify = time()

    def stop(self):
        # Send stopping
        return

    def log(self, message=None):
        # Print log message
        return
