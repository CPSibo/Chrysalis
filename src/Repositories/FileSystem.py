import attr
import time
import pathlib
import re

from Repositories.Repository import Repository, RepositoryTypes



@attr.s
class FileSystem(Repository):

    # region Initialized attributes

    path : str = attr.ib()

    # endregion


    # region Attributes

    name : str = None
    ext : str = None
    directory : str = None
    modified : str = None
    size : int = None

    # endregion



    # region Constructors

    def __attrs_post_init__(self):
        self.type = RepositoryTypes.FILE
        self.source = 'os'

        path_obj = pathlib.Path(self.path)

        self.name = path_obj.stem
        self.ext = path_obj.suffix[1:]
        self.all_ext = re.match(r'^.+?\.(.+)$', path_obj.name).group(1) if path_obj.is_file() else ''
        self.directory = str(path_obj.parent)
        self.modified = time.ctime(path_obj.stat().st_mtime)
        self.size = path_obj.stat().st_size

    # endregion