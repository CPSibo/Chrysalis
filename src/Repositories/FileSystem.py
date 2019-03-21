import attr
import time
import pathlib
import re

from Repositories.Repository import Repository, RepositoryTypes
from .Repository import RegisteredRepository

@RegisteredRepository
@attr.s
class FileSystem(Repository):

    # region Initialized attributes

    path : str = attr.ib(default=None)

    # endregion


    # region Attributes

    source : str = 'os'
    type = RepositoryTypes.FILE

    # endregion



    # region Constructors

    def __attrs_post_init__(self):
        self.name : str = None
        self.ext : str = None
        self.directory : str = None
        self.modified : str = None
        self.size : int = None

        self.get_path_info()

    # endregion



    # region Functions

    def get_path_info(self):
        if self.path is not None and len(self.path) > 0:
            path_obj = pathlib.Path(self.path)

            self.name = path_obj.stem
            self.ext = path_obj.suffix[1:]
            self.all_ext = re.match(r'^.+?\.(.+)$', path_obj.name).group(1) if path_obj.is_file() else ''
            self.directory = str(path_obj.parent)
            self.modified = time.ctime(path_obj.stat().st_mtime)
            self.size = path_obj.stat().st_size
            
    # endregion