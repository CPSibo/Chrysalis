import os
import json

from Repositories.Repository import Repository, RepositoryTypes
from Utilities.Logger import Logger
from .Repository import RegisteredRepository

@RegisteredRepository
class TVDB(Repository):
    """
    API wrapper for TheTVDB.com.

    Attributes:
        base_url (str): Minimal URL for the API.
        username (str): API username.
        user_key (str): Secret key for the user.
        api_key (str): Secret API key for the user.
        jwt (str): JWT returned from login.
    """

    source: str = 'tvdb'
    type: RepositoryTypes = RepositoryTypes.EPISODE | RepositoryTypes.SERIES



    def __init__(self):
        self.base_url: str = 'https://api.thetvdb.com/'
        self.api_key: str = None
        self.jwt: str = None
        self.username = os.getenv("tvdb_username")
        self.user_key = os.getenv("tvdb_userkey")
        self.api_key = os.getenv("tvdb_apikey")



    def login(self):
        """
        Pass the user credentials to receive a JWT.
        """

        Logger.log(r'API', r'Logging in...')

        request_data = {
            'username': self.username,
            'userkey': self.user_key,
            'apikey': self.api_key,
        }

        encoded_data = json.dumps(request_data).encode('utf-8')

        response = self.http.request(
            'POST', 
            self.base_url + 'login',
            body=encoded_data,
            headers={'Content-Type': 'application/json'}
        )

        response_data = json.loads(response.data.decode('utf-8'))

        self.jwt = response_data['token']



    def get_series(self, series_id: int):
        """
        Query series information.
        
        Args:
            series_id (int): Unique ID of the series.
        
        Returns:
            dict: Series infomation.
        """

        Logger.log(r'API', r'Querying series...')

        response = self.http.request(
            'GET', 
            self.base_url + 'series/' + str(series_id),
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.jwt
            }
        )

        response_data = json.loads(response.data.decode('utf-8'))

        return response_data['data']



    def get_series_episodes(self, series_id: int):
        """
        Query episode information for series.

        Automatically retrieves all pages.
        
        Args:
            series_id (int): Unique ID of the series.
        
        Returns:
            list: List of dicts for episodes.
        """

        Logger.log(r'API', r'Querying episodes...')

        page = 1

        episodes = []

        while True:
            response = self.http.request(
                'GET', 
                self.base_url + 'series/' + str(series_id) + '/episodes?page=' + str(page),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + self.jwt
                }
            )

            response_data = json.loads(response.data.decode('utf-8'))

            episodes.extend(response_data['data'])

            if response_data['links']['next'] is None or page == response_data['links']['last']:
                break
            
            page += 1

        episodes = list({v['episodeName']:v for v in episodes if v['episodeName'] is not None and v['episodeName'] != ''}.values())

        return episodes



    def match_episode(self, episodes: list, title: str):
        """
        Attempts to find the series' episode that
        matches the given title from youtube-dl.
        
        Args:
            episodes (list): List of dicts of episode information.
            title (str): The title to match against.
        
        Returns:
            dict: The matched episode.
        """

        import pylev

        for episode in episodes:
            episode['__distance'] = pylev.recursive_levenshtein(episode['episodeName'], title)
            episode['__ratio'] = 1 - (episode['__distance'] / len(episode['episodeName']))

        threshold = 0.8

        filtered_episodes = [item for item in episodes if item['__ratio'] >= threshold]

        sorted_episodes = sorted(
            filtered_episodes, 
            key=lambda x: x['__distance']
        )

        return sorted_episodes[0]