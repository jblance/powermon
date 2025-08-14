from enum import Enum

class ActionType(Enum):
    """ enum of valid types of Actions """
    BASIC = 'basic'
    TEMPLATE = 'template'
    CACHE_QUERY = 'cache_query'