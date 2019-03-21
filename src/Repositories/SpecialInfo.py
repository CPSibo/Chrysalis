import attr

from Repositories.Repository import Repository, RepositoryTypes
from .Repository import RegisteredRepository

@RegisteredRepository
@attr.s
class SpecialInfo(Repository):
    """
    Bespoke DB source for Chrysalis info.
    """


    # region Constants

    _UNKNOWN_SEASON = 'Unknown'
    _SPECIAL_SEASON = 'Special'

    # endregion



    # region Initialized attributes

    season_number = attr.ib(type=int, default=-1)

    # endregion



    # region Attributes

    source = 'chrysalis'
    type = RepositoryTypes.SPECIAL

    # endregion



    # region Constructors

    def __attrs_post_init__(self):
        self.season = self._UNKNOWN_SEASON
        self.set_season()

    # endregion



    # region Functions

    def set_season(self):
        """Set the season folder name."""
        
        if self.season_number < 0:
            self.season = self._UNKNOWN_SEASON
        elif self.season_number == 0:
            self.season = self._SPECIAL_SEASON
        else:
            self.season = 'Season {:02d}'.format(self.season_number)

    # endregion