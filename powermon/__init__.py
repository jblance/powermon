# import locale
import gettext
import pathlib

from .version import __version__

__all__: list = ['__version__']

LOCALE_PATH = f"{pathlib.Path(__file__).parent}/locale/"
lang = gettext.translation(domain="powermon", localedir=LOCALE_PATH, languages=['en'])
lang.install()
_ = lang.gettext
