import attr
import time
import pathlib
import re

@attr.s
class FileSystem:

    # region Initialized attributes

    path = attr.ib(type=str)

    # endregion


    # region Attributes

    name = None
    ext = None
    directory = None
    modified = None
    size = None

    # endregion



    # region Constructors

    def __attrs_post_init__(self):
        path_obj = pathlib.Path(self.path)

        self.name = path_obj.stem
        self.ext = path_obj.suffix[1:]
        self.all_ext = re.match(r'^.+?\.(.+)$', path_obj.name).group(1) if path_obj.is_file() else ''
        self.directory = str(path_obj.parent)
        self.modified = time.ctime(path_obj.stat().st_mtime)
        self.size = path_obj.stat().st_size

    # endregion