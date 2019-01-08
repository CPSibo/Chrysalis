import attr

@attr.s
class SpecialInfo:

    # region Constants

    _UNKNOWN_SEASON = 'Unknown'
    _SPECIAL_SEASON = 'Special'

    # endregion



    # region Initialized attributes

    season_number = attr.ib(type=int)

    # endregion



    # region Attributes

    season = _UNKNOWN_SEASON

    # endregion



    # region Constructors

    def __attrs_post_init__(self):
        self.set_season()

    # endregion



    # region Functions

    def set_season(self):
        """Set the season folder name."""
        season = 'Season {:02d}'.format(self.season_number)

        if season == 'Season 00':
            season = self._SPECIAL_SEASON

        self.season = season

    # endregion