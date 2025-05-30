from enum import Enum

class InstructionType(Enum):
    """ enum of valid types of Instructions """
    BASIC = 'basic'
    TEMPLATE = 'template'
    CACHE_QUERY = 'cache_query'