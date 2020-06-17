from .protocol import AbstractProtocol


class pi30(AbstractProtocol):
    def __init__(self, *args, **kwargs) -> None:
        print(__name__)
        print(args)
        print(kwargs)

    def get_protocol(self):
        return b'PI30'
