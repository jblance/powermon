from enum import Enum

class TaskType(Enum):
    """ enum of valid types of Tasks """
    BASIC = 'basic'
    TEMPLATE = 'template'
    CACHE_QUERY = 'cache_query'