# region Imports

import attr
import pathlib
import re
import itertools

from Utilities.Logger import Logger
from Repositories.FileSystem import FileSystem
from Repositories import REPOSITORIES
from Destinations import DESTINATIONS

# endregion



@attr.s
class PostProcessor:
    """
    Controlling class for the renaming facilities.

    Attributes:
        file (str): Path to the file being processed.
        settings (Subscription): The subscription settings
            used for this file.

        path_info (pathlib.Path): Path object for the file.
        series (dict): Series info for the file.
        episode (dict): Episode info for the file.
    """

    file: str = attr.ib()
    settings = attr.ib()



    def __attrs_post_init__(self):
        self.path_info: pathlib.Path = None
        self.series: dict = None
        self.episode: dict = None
        self.special_values = None
        self.repositories: list = []


        
    def run(self):
        """
        Runs all post-processing on the file.
        
        Returns:
            str: Path to the post-processed output directory.
        """

        self.path_info = pathlib.Path(self.file)

        Logger.log(r'PostProcessor', r'Processing {}...'.format(self.path_info.parent), 1)

        if self.settings.post_processing.repositories is not None and 'tvdb' in self.settings.post_processing.repositories:
            self.get_api_info()

        if self.settings.post_processing.pattern is not None:
            self.special_values = re.match(self.settings.post_processing.pattern, str(self.path_info))

        if self.settings.post_processing.subtitle is not None:
            self.rename_subtitles()

        if self.settings.post_processing.thumbnail is not None:
            self.rename_thumbnails()

        if self.settings.post_processing.description is not None:
            self.rename_description()

        if self.settings.post_processing.video is not None:
            self.path_info = self.rename_video()

        if self.settings.post_processing.episode_folder is not None:
            new_folder = self.rename_folder()
        else:
            new_folder = self.path_info.parent

        self.path_info = new_folder / self.path_info.name

        
        if self.settings.post_processing.output_directory:
            self.move_from_staging_area(new_folder)

        if self.settings.post_processing.real_destinations:
            destination = self.settings.post_processing.real_destinations[0]
            
            if destination:
                destination.run(self)

        Logger.tabs -= 1

        return new_folder



    def move_from_staging_area(self, current_path):
        """
        Moves the post-processed folder from the staging area
        to the final path specified by the subscription.
        """

        out_dir = self.settings.post_processing.output_directory

        pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True) 

        final_dir = out_dir + '/' + current_path.name

        current_path.rename(final_dir)

        self.path_info = pathlib.Path(final_dir) / self.path_info.name

        Logger.log(r'PostProcessor', r'Refoldered to {}'.format(final_dir))



    def get_api_info(self):
        """
        Retrieves the API info for the file.
        """

        from Repositories.TVDB import TVDB
        
        Logger.log(r'API', r'Querying...', 1)

        api = TVDB()
        api.login()

        self.series = api.get_series(self.settings.post_processing.series_id)
        episodes = api.get_series_episodes(self.settings.post_processing.series_id)

        if episodes is None or len(episodes) == 0:
            Logger.log(r'API', r'No episodes returned!', -1)
            return -1

        file_matches = re.match(self.settings.post_processing.pattern, str(self.path_info))

        self.episode = api.match_episode(episodes, file_matches.group('episodeName'))

        Logger.tabs -= 1


    
    def youtubedl_sanitize_filename(self, s, restricted=False, is_id=False):
        """Sanitizes a string so it could be used as part of a filename.
        If restricted is set, use a stricter subset of allowed characters.
        Set is_id if this is not an arbitrary string, but an ID that should be kept
        if possible.
        """
        # needed for sanitizing filenames in restricted mode
        ACCENT_CHARS = dict(zip('ÂÃÄÀÁÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖŐØŒÙÚÛÜŰÝÞßàáâãäåæçèéêëìíîïðñòóôõöőøœùúûüűýþÿ',
            itertools.chain('AAAAAA', ['AE'], 'CEEEEIIIIDNOOOOOOO', ['OE'], 'UUUUUYP', ['ss'],
                            'aaaaaa', ['ae'], 'ceeeeiiiionooooooo', ['oe'], 'uuuuuypy')))
                            
        def replace_insane(char):
            if restricted and char in ACCENT_CHARS:
                return ACCENT_CHARS[char]
            if char == '?' or ord(char) < 32 or ord(char) == 127:
                return ''
            elif char == '"':
                return '' if restricted else '\''
            elif char == ':':
                return '_-' if restricted else ' -'
            elif char in '\\/|*<>':
                return '_'
            if restricted and (char in '!&\'()[]{}$;`^,#' or char.isspace()):
                return '_'
            if restricted and ord(char) > 127:
                return '_'
            return char

        # Handle timestamps
        s = re.sub(r'[0-9]+(?::[0-9]+)+', lambda m: m.group(0).replace(':', '_'), s)
        result = ''.join(map(replace_insane, s))
        if not is_id:
            while '__' in result:
                result = result.replace('__', '_')
            result = result.strip('_')
            # Common case of "Foreign band name - English song title"
            if restricted and result.startswith('-_'):
                result = result[2:]
            if result.startswith('-'):
                result = '_' + result[len('-'):]
            result = result.lstrip('.')
            if not result:
                result = '_'
        return result


    def replace_values(self, info: FileSystem, template: str):
        """
        Substitutes formatting tokens with their real values.
        
        Args:
            info (FileSystem): FileSystem DB info for the file.
            template (str): Output format template.
        
        Returns:
            str: Substituted output template.
        """

        template_matches = re.findall(r'({(series|episode|file|special)\.(\w+)(:[^}]+?)?})', template)

        replaced_template = template

        for match in template_matches:
            replaced_template = self.replace_value(info, match, replaced_template)
            
        return replaced_template

    
    def replace_value(self, info: FileSystem, match: re.match, replaced_template: str):
        """
        Replaces a formatting token with its real value.
        
        Args:
            info (FileSystem): FileSystem DB info for the file.
            match (match): The regex match of the token.
            replaced_template (str): Output format template.
        
        Returns:
            str: Substituted output template.
        """

        replacement_type = match[1]
        replacement_item = match[2]
        replacement_format = match[3] if len(match) > 2 else None

        value = None

        if replacement_type == 'series':
            value = self.series[replacement_item]
        elif replacement_type == 'episode':
            value = self.episode[replacement_item]
        elif replacement_type == 'file':
            value = getattr(info, replacement_item)
        elif replacement_type == 'special' and self.special_values is not None:
            value = self.special_values.group(replacement_item)

        formatted_value = value

        if replacement_format is not None and replacement_format is not '':
            try:
                formatted_value = (r'{' + replacement_format + r'}').format(value)
            except ValueError:
                formatted_value = (r'{' + replacement_format + r'}').format(int(value))

        replaced_template = replaced_template.replace(match[0], formatted_value)

        return replaced_template



    def rename_file(self, path: str, template: str, sanitize: bool = True):
        """
        Renames a given file according to a given template.
        
        Args:
            path (str): Path to the file to rename.
            template (str): Output template to rename the file by.
            sanitize (bool, optional): Defaults to True. True to
                replace path delimiters within the substituted
                template to avoid unexpected directories.
        
        Returns:
            str: The renamed path to the file.
        """

        if not path.exists(): 
            return

        info = FileSystem(path = path)

        replaced_template = self.replace_values(info, template)

        if sanitize:
            replaced_template = replaced_template.replace('/', '_').replace('\\', '_')

        new_filename = path.with_name(replaced_template)
            
        path.rename(new_filename)

        Logger.log(r'PostProcessor', r'{} => {}'.format(path.name, replaced_template))

        return new_filename



    def rename_video(self):
        """
        Renames the video file.
        """

        return self.rename_file(
            self.path_info, 
            self.settings.post_processing.video
        )


    def rename_thumbnails(self):
        """
        Renames the video thumbnails.
        """

        suffixes = [
            '.jpg',
            '.jpeg',
            '.png',
            '.btm',
        ]

        for suffix in suffixes:
            self.rename_file(
                self.path_info.with_suffix(suffix), 
                self.settings.post_processing.thumbnail
            )


    def rename_description(self):
        """
        Renames the video description.
        """

        return self.rename_file(
            self.path_info.with_suffix('.description'), 
            self.settings.post_processing.description
        )


    def rename_subtitles(self):
        """
        Renames the video subtitles.
        """

        suffixes = [
            '*.srt',
            '*.ass',
            '*.vtt',
            '*.lrc',
        ]

        for suffix in suffixes:
            for path in self.path_info.parent.glob(suffix):
                self.rename_file(
                    path, 
                    self.settings.post_processing.subtitle
                )


    def rename_folder(self):
        """
        Renames the video folder.
        
        Returns:
            str: Path to the renamed folder.
        """

        return self.rename_file(
            self.path_info.parent, 
            self.settings.post_processing.episode_folder
        )
