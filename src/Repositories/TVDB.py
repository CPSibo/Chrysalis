import os
import urllib3
import json

from Utilities.Logger import Logger

class TVDB:
    base_url = 'https://api.thetvdb.com/'
    username = None
    user_key = None
    api_key = None
    jwt = None
    http = None

    def __init__(self):
        self.username = os.getenv("tvdb_username")
        self.user_key = os.getenv("tvdb_userkey")
        self.api_key = os.getenv("tvdb_apikey")

        urllib3.disable_warnings()
        self.http = urllib3.PoolManager()

    def login(self):
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

    def get_series(self, series_id):
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

    def get_series_episodes(self, series_id):
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

    def match_episode(self, episodes, title):
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
