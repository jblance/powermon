import logging

log = logging.getLogger('powermon')


class print():
    def __init__(self, *args, **kwargs) -> None:
        log.info('Using output processor: print')
        log.debug(f'processor.print __init__ kwargs {kwargs}')
        self._data = kwargs['results']

    def process(self):
        if self._data is None:
            return
        print(f"{'Parameter':<30}\t{'Value':<15} Unit")
        for key in self._data:
            value = self._data[key][0]
            unit = self._data[key][1]
            print(f'{key:<30}\t{value:<15}\t{unit:<4}')
