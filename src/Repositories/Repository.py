import attr
import urllib3
from enum import Flag, auto



REPOSITORIES = []

def RegisteredRepository(cls):
    REPOSITORIES.append(cls)
    return cls



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

    def __init__(self):
        urllib3.disable_warnings()
        self.http: urllib3.PoolManager = urllib3.PoolManager()