# import locale
import gettext
import pathlib

from .config.powermon_config import PowermonConfig

from .mqttbroker.mqttbroker import MqttBroker
from .version import __version__

__all__: list = ['PowermonConfig', 'MqttBroker', '__version__']

LOCALE_PATH = f"{pathlib.Path(__file__).parent}/locale/"
lang = gettext.translation(domain="powermon", localedir=LOCALE_PATH, languages=['en'])
lang.install()
_ = lang.gettext
