import attr

@attr.s
class Subscription:
    @attr.s
    class Logging:
        path = attr.ib(type=str)
        append = attr.ib(type=bool)

    @attr.s
    class YoutubedlConfig:
        archive = attr.ib(type=str)
        metadata_format = attr.ib(type=str)
        output_format = attr.ib(type=str)
        config = attr.ib(type=str)
        extra_commands = attr.ib(type=str)

    @attr.s
    class PostProcessing:
        output_directory = attr.ib(type=str)

        db = attr.ib(type=str)
        series_id = attr.ib(type=int)

        pattern = attr.ib(type=str)

        season_folder = attr.ib(type=str)
        episode_folder = attr.ib(type=str)
        video = attr.ib(type=str)
        subtitle = attr.ib(type=str)
        thumbnail = attr.ib(type=str)
        description = attr.ib(type=str)

    dict_config = attr.ib(type=dict)

    name = None
    url = None

    logging = None
    youtubedl_config = None
    post_processing = None



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

            db = self.get_setting('post-processing.db'),
            series_id = self.get_setting('post-processing.series id'),

            pattern = self.get_setting('post-processing.pattern'),

            season_folder = self.get_setting('post-processing.season folder'),
            episode_folder = self.get_setting('post-processing.episode folder'),
            video = self.get_setting('post-processing.video'),
            subtitle = self.get_setting('post-processing.subtitle'),
            thumbnail = self.get_setting('post-processing.thumbnail'),
            description = self.get_setting('post-processing.description'),
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
    