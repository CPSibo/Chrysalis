from .Destination import DESTINATIONS

# Import all classes in this directory so that classes with @register_class are registered. 

from os.path import basename, dirname, join
from pathlib import Path
from glob import glob
pwd = dirname(__file__)
for x in glob(join(pwd, '*.py')):
    name = basename(x)[:-3]
    module = Path(x).parent.name
    if not name.startswith('__'):
        __import__(module + '.' + name, globals(), locals())


__all__ = [
    'DESTINATIONS'
]