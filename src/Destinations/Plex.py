import os
import time
import ffmpeg
import pathlib

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

        self.metadata = {
            'summary': {
                'wanted': False,
                'provided value': None,
                'found value': None,
            },
            'originallyAvailableAt': {
                'wanted': False,
                'provided value': None,
                'found value': None,
            },
        }



    def run(self, postprocessor):
        Logger.log(r'Plex', r'Processing {}...'.format(postprocessor.path_info.parent), 1)

        self.postprocessor = postprocessor

        self.login()

        if "metadata" in self.postprocessor.settings.post_processing.destination:
            self.set_metadata()



    def login(self):
        Logger.log(r'Plex', r'Logging in...', 1)

        self.session = PlexServer(self.url, self.token)

        Logger.tabs -= 1



    def set_metadata(self):
        Logger.log(r'Plex', r'Setting metadata...', 1)

        self.parse_metadata_settings()

        episode = self.get_episode()

        if not episode:
            return -1

        # Try to pull the metadata out of the file itself, first.
        self.try_file_metadata()

        # If we couldn't get the description from the file, try a .description file.
        if not self.metadata['summary']['found value'] and self.metadata['summary']['wanted']:
            self.try_description_file()
             
        values = {}

        for item in self.metadata:
            if self.metadata[item]['found value']:
                Logger.log(r'Plex', r'Setting metadata: {} = {}...'.format(item, self.metadata[item]['found value'][:20]))
                values[item + '.value'] = self.metadata[item]['found value']
                values[item + '.locked'] = 1

        # Plex seems to have a race condition if you set values before it's
        # finished the library scan. If the scan finishes afterwards, it seems
        # like the values get reset.
        episode.section().cancelUpdate()
        time.sleep(10)

        episode.edit(**values)

        Logger.log(r'Plex', r'Metadata set.')

        Logger.tabs -= 1


    def get_episode(self):
        destination_settings = self.postprocessor.settings.post_processing.destination

        section_name = destination_settings["section"]
        series_name = destination_settings["series"] or self.postprocessor.settings.name

        if not section_name:
            Logger.log(r'Plex', r'No "section" set!')
            return None

        if not series_name:
            Logger.log(r'Plex', r'No "series" set!')
            return None

        section = self.session.library.section(section_name)

        if not section:
            Logger.log(r'Plex', r'"{}" section not found!'.format(section_name))
            return None
        
        # Make sure Plex knows about our new video.
        section.update()
        time.sleep(3)

        series = None
        tries = 0

        # Grab the show.
        while not series and tries < 10:
            try:
                series = section.get(series_name)
            except exceptions.NotFound:
                # It can take plex a few seconds to 
                # find the show if it's new.
                tries += 1
                section.update()
                time.sleep(10 * tries)


        if not series:
            Logger.log(r'Plex', r'"{}" series not found!'.format(series_name))
            return None

        episode = None
        tries = 0


        while not episode and tries < 10:
            try:
                episodes = series.episodes()
                episodes = [episode for episode in episodes \
                    if pathlib.Path(episode.locations[0]).name == self.postprocessor.path_info.name]
                episode = episodes[0]
            except:
                # It can take plex a few seconds to 
                # find the episode.
                tries += 1
                section.update()
                time.sleep(10 * tries)

        if not episode:
            Logger.log('Plex', "Couldn't find episode!")
            raise Exception("Couldn't find episode!")
            return None

        return episode

    

    def parse_metadata_settings(self):
        destination_settings = self.postprocessor.settings.post_processing.destination
        metadata_settings = destination_settings["metadata"]

        for item in self.metadata:
            if item in metadata_settings:
                self.parse_metadata_setting(item, metadata_settings[item])



    def parse_metadata_setting(self, key, setting):
        item = self.metadata[key]

        if type(setting) is bool:
            item['wanted'] = setting
        else:
            item['provided value'] = setting
            item['found value'] = setting


    def try_file_metadata(self):
        try:
            file_metadata = ffmpeg.probe(str(self.postprocessor.path_info))
        except:
            None

        if file_metadata:
            if self.metadata['summary']['wanted']:
                try:
                    self.metadata['summary']['found value'] = file_metadata['format']['tags']['DESCRIPTION']
                except:
                    Logger.log(r'Plex', r'Couldn\'t read description from tags.')

            if self.metadata['originallyAvailableAt']['wanted']:
                try:
                    temp_date = file_metadata['format']['tags']['DATE']
                    self.metadata['originallyAvailableAt']['found value'] = temp_date[0:4] \
                        + '-' + temp_date[4:6] + '-' + temp_date[6:8]
                except:
                    Logger.log(r'Plex', r'Couldn\'t read date from tags.')


    def try_description_file(self):
        description_file_path = self.postprocessor.path_info.with_suffix('.description')

        try:
            with open(description_file_path, 'r') as myfile:
                self.metadata['summary']['found value'] = myfile.read()
        except:
            Logger.log(r'Plex', r'Couldn\'t read from *.description file.')

        description_file_path = self.postprocessor.path_info.parent / 'description.txt'

        try:
            with open(description_file_path, 'r') as myfile:
                self.metadata['summary']['found value'] = myfile.read()
        except:
            Logger.log(r'Plex', r'Couldn\'t read from description.txt file.')