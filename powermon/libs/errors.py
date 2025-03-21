""" a collection of powermon specific exceptions """


class BLEResponseError(Exception):
    """ Exception for errors with BLE response """


class ConfigError(Exception):
    """ Exception for invaild configurations """

class ConfigNeedsUpdatingError(Exception):
    """ Exception for invalid configurations due to a breaking change """


class PowermonProtocolError(Exception):
    """ Exception for errors with protocol definitions """


class PowermonWIP(Exception):
    """ Exception for work not yet done """


class InvalidResponse(Exception):
    """ Exception for invalid responses """


class InvalidCRC(Exception):
    """ Exception for invalid crc """


class CommandDefinitionMissing(Exception):
    """ Exception for missing / not found command definition """


class CommandDefinitionIncorrect(Exception):
    """ Exception for errors in command definition """


class CommandError(Exception):
    """ Exception for errors with commands """


class CommandExecutionFailed(Exception):
    """ Exception for errors with execution of commands """
