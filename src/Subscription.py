# region Imports

import attr
import os

# endregion



@attr.s
class Subscription:
    """
    Collection of settings for a given subscription.

    Attributes:
        dict_config (dict): Dictionary of the settings to import.
    """

    @attr.s
    class Logging:
        path: str = attr.ib()
        append: bool = attr.ib()

    @attr.s
    class YoutubedlConfig:
        archive: str = attr.ib()
        metadata_format: str = attr.ib()
        output_format: str = attr.ib()
        config: str = attr.ib()
        extra_commands: str = attr.ib()

    @attr.s
    class PostProcessing:
        output_directory: str = attr.ib()

        series_id: int = attr.ib()

        repositories: list = attr.ib()

        pattern: str = attr.ib()

        season_folder: str = attr.ib()
        episode_folder: str = attr.ib()
        video: str = attr.ib()
        subtitle: str = attr.ib()
        thumbnail: str = attr.ib()
        description: str = attr.ib()

        def __attrs_post_init__(self):
            for repo in self.repositories:
                importlib.import_module('Repositories.' + repo)

    dict_config = attr.ib(type=dict)

    name: str = None
    url: str = None

    logging: Logging = None
    youtubedl_config: YoutubedlConfig = None
    post_processing: PostProcessing = None

    staging_directory: str = None



    def __attrs_post_init__(self):
        self.name = self.get_setting('name')
        self.url = self.get_setting('url')

        self.logging = self.Logging(
            path = self.get_setting('logging.path'),
            append = self.get_setting('logging.append')
        )

        self.youtubedl_config = self.YoutubedlConfig(
            archive = self.get_setting('youtube-dl config.archive'),
            metadata_format = self.get_setting('youtube-dl config.metadata format'),
            output_format = self.get_setting('youtube-dl config.output format'),
            config = self.get_setting('youtube-dl config.config'),
            extra_commands = self.get_setting('youtube-dl config.extra commands'),
        )

        self.post_processing = self.PostProcessing(
            output_directory = self.get_setting('post-processing.output directory'),

            series_id = self.get_setting('post-processing.series id'),

            repositories = self.get_setting('post-processing.repositories'),

            pattern = self.get_setting('post-processing.pattern'),

            season_folder = self.get_setting('post-processing.season folder'),
            episode_folder = self.get_setting('post-processing.episode folder'),
            video = self.get_setting('post-processing.video'),
            subtitle = self.get_setting('post-processing.subtitle'),
            thumbnail = self.get_setting('post-processing.thumbnail'),
            description = self.get_setting('post-processing.description'),
        )

        self.staging_directory = os.path.join(
			os.getenv('staging_directory'), 
			self.name
		)



    def get_setting(self, setting: str):
        if self.dict_config is None:
            return None

        if setting is None or len(setting) == 0:
            return None

        path = self.dict_config

        for part in setting.split('.'):
            if part not in path:
                return None

            path = path[part]

        return path
    