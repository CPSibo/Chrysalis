import attr
import urllib3
from enum import Flag, auto



class RepositoryTypes(Flag):
    EPISODE =   auto()
    SERIES =    auto()
    FILE =      auto()
    SPECIAL =   auto()



@attr.s
class Repository:
    """
    Generic class for a repository of info about
    a given file.
    
    Attributes:
        http (urllib3.PoolManager): PoolManager for class use.
    """

    type: RepositoryTypes = None
    source: str = None
    http: urllib3.PoolManager = None


    def __init__(self):
        urllib3.disable_warnings()
        self.http = urllib3.PoolManager()
