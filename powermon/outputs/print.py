import logging

log = logging.getLogger('powermon')


class print():
    def __init__(self, *args, **kwargs) -> None:
        log.info('Using output processor: print')
        log.debug(f'processor.print __init__ kwargs {kwargs}')
        results = kwargs['results']
        print(f"{'Parameter':<30}\t{'Value':<15} Unit")
        for key in results:
            value = results[key][0]
            unit = results[key][1]
            print(f'{key:<30}\t{value:<15}\t{unit:<4}')
