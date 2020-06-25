import logging

log = logging.getLogger('powermon')


class mqtt():
    def __init__(self, *args, **kwargs) -> None:
        log.info('Using output processor: mqtt')
        log.debug(f'processor.mqtt __init__ kwargs {kwargs}')
        _data = kwargs['results']
        if _data is None:
            return

        # TODO: complete mqtt output processor
        print(f"{'Parameter':<30}\t{'Value':<15} Unit")
        for key in _data:
            value = _data[key][0]
            unit = _data[key][1]
            print(f'{key:<30}\t{value:<15}\t{unit:<4}')
