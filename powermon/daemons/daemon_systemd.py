import logging
from time import time
try:
    from cysystemd import journal
    from cysystemd.daemon import Notification, notify
except ModuleNotFoundError as exception:
    print(
        f"error: {exception}, try 'pip install cysystemd' (which may need 'apt install build-essential libsystemd-dev'), see https://pypi.org/project/cysystemd/ for further info"
    )
    exit(1)

from .daemon import Daemon

# Set-up logger
log = logging.getLogger("daemon")

class DaemonSystemd(Daemon):

    def __init__(self, keepalive):
        super().__init__(keepalive=keepalive)
        self.type = 'systemd'


    def initialize(self):
        """ Daemon initialization activities """
        notify(Notification.READY)
        self.last_notify = time()

    def watchdog(self):
        elapsed = time() - self.last_notify
        if (elapsed) > self.keepalive:
            notify(Notification.WATCHDOG)
            self.last_notify = time()
            journal.write(f"Daemon notify at {self.last_notify}")

    def notify(self, status="OK"):
        # Send status
        self.last_notify = time()
        notify(Notification.STATUS, status)

    def stop(self):
        # Send stopping
        notify(Notification.STOPPING)

    def log(self, message=None):
        # Print log message
        if message is not None:
            journal.write(message)

