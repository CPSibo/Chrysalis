import os
import time
import ffmpeg

from .Destination import Destination
from .Destination import RegisteredDestionation
from Utilities.Logger import Logger
from plexapi.server import PlexServer
from plexapi import exceptions

@RegisteredDestionation
class Plex(Destination):
    from PostProcessor import PostProcessor

    destination = 'plex'



    def __init__(self):
        self.root_path: str = ''
        self.username: str = ''
        self.password: str = ''
        self.session: object = None
        self.url: str = os.getenv("plex_url")
        self.token: str = os.getenv("plex_token")
        self.postprocessor: self.PostProcessor = None



    def run(self, postprocessor):
        Logger.log(r'Plex', r'Processing {}...'.format(postprocessor.path_info.parent), 1)

        self.postprocessor = postprocessor

        self.login()
        self.set_metadata()



    def login(self):
        Logger.log(r'Plex', r'Logging in...', 1)

        self.session = PlexServer(self.url, self.token)

        Logger.tabs -= 1



    def set_metadata(self):
        Logger.log(r'Plex', r'Setting metadata...', 1)

        section_name = self.postprocessor.settings.post_processing.destination["section"]
        series_name = self.postprocessor.settings.post_processing.destination["series"] or self.postprocessor.settings.name

        if not section_name:
            Logger.log(r'Plex', r'No "section" set!')
            return -1

        if not series_name:
            Logger.log(r'Plex', r'No "series" set!')
            return -1

        section = self.session.library.section(section_name)

        if not section:
            Logger.log(r'Plex', r'"{}" section not found!'.format(section_name))
            return -1
        
        # Make sure Plex knows about our new video.
        section.update()

        series = None
        tries = 0

        # Grab the show.
        while not series and tries < 30:
            try:
                series = section.get(series_name)
            except exceptions.NotFound:
                time.sleep(1)
                tries += 1


        if not series:
            Logger.log(r'Plex', r'"{}" series not found!'.format(series_name))
            return -1

        episode = series.episodes()[0]

        description = None
        date = None

        # Try to pull the metadata out of the file itself, first.
        try:
            metadata = ffmpeg.probe(str(self.postprocessor.path_info))
        except:
            None

        if metadata:
            try:
                description = metadata['format']['tags']['DESCRIPTION']
            except:
                None

            try:
                date = metadata['format']['tags']['DATE']
                date = date[0:4] + '-' + date[4:6] + '-' + date[6:8]
            except:
                None

        # If we couldn't get the description from the file, try a .description file.
        if not description:
            description_file_path = self.postprocessor.path_info.with_suffix('.description')

            try:
                with open(description_file_path, 'r') as myfile:
                    description = myfile.read()
            except:
                None
                


        values = {
            'summary.value': description or '',
            'originallyAvailableAt.value': date or '1900-01-01',
        }

        episode.edit(**values)

        Logger.log(r'Plex', r'Metadata set.')

        Logger.tabs -= 1