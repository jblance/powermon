# import locale
import gettext
import pathlib

from .config.powermon_config import PowermonConfig
from .mqttbroker.mqttbroker import MqttBroker
from .daemons.daemon import Daemon
from .version import __version__

LOCALE_PATH = f"{pathlib.Path(__file__).parent}/locale/"
lang = gettext.translation(domain="powermon", localedir=LOCALE_PATH, languages=['en'], fallback=['en_US'])
lang.install()
_ = lang.gettext
