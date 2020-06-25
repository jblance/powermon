import logging

log = logging.getLogger('powermon')


class influx_mqtt():
    def __init__(self, *args, **kwargs) -> None:
        log.info('Using output processor: influx_mqtt')
        log.debug(f'processor.influx_mqtt __init__ kwargs {kwargs}')
        _data = kwargs['results']
        _tag = ''
        if _data is None:
            return

        # TODO: complete influx output processor
        # print(f"{'Parameter':<30}\t{'Value':<15} Unit")
        # for key in _data:
        #    value = _data[key][0]
        #    unit = _data[key][1]
        #    print(f'{key:<30}\t{value:<15}\t{unit:<4}')

        # Build array of Influx Line Protocol messages
        msgs = []
        # Loop through responses
        for key in _data:
            value = _data[key][0]
            # unit = _data[key][1]
            # Message format is: mpp-solar,command=QPGS0 max_charger_range=120.0
            msg = {'topic': 'mpp-solar', 'payload': f'mpp-solar,command={_tag} {key}={value}'}
            msgs.append(msg)
        # publish.multiple(msgs, hostname=args.broker)
        print(msgs)
