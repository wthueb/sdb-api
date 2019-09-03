import json
from urllib.parse import quote

import requests


class SDB:
    BASE_URL = 'http://api.sportsdatabase.com/{sport}/query.json?sdql={sdql}&output=json&api_key={api_key}'

    SDQL_PARAMS = ('ats margin', 'ats streak', 'cdivision', 'coach', 'completions',
                   'conference', 'date', 'day', 'division', 'dpa', 'dps', 'first downs',
                   'fourth downs attempted', 'fourth downs made', 'full name', 'fumbles',
                   'fumbles lost', 'game number', 'game type', 'interceptions', 'line',
                   'losses', 'margin', 'margin after the first', 'margin after the third',
                   'margin at the half', 'matchup losses', 'matchup wins', 'month', 'opponents',
                   'ou margin', 'ou streak', 'overtime', 'passes', 'passing yards', 'penalties',
                   'penalties yards', 'penalty yards', 'playoffs', 'points', 'quarter scores',
                   'rank', 'rest', 'rot', 'round', 'rushes', 'rushing yards', 'school',
                   'season', 'seed', 'site', 'site streak', 'start time', 'streak', 'team',
                   'third downs attempted', 'third downs made', 'time of possession', 'total',
                   'turnover margin', 'turnovers', 'week', 'wins')

    with open('abbrvs.json', 'r') as f:
        TEAM_ABBRVS = json.load(f)

    def __init__(self, sport: str, api_key: str = 'guest') -> None:
        supported = ('ncaafb',)

        if sport not in supported:
            raise ValueError(f'the only supported sports are currently: {supported}')

        self.SPORT = sport
        self.API_KEY = api_key

    def query(self, sdql: str) -> dict:
        encoded = _verify_and_encode_sdql(sdql)

        return _request(encoded)

    def _verify_and_encode_sdql(self, sdql: str) -> str:
        if not sdql:
            raise ValueError('sdql query cannot be empty')

        if '@' in sdql:
            if sdql.count('@') > 1:
                raise ValueError(f'sdql query cannot contain two @ symbols: {sdql}')

            cols, kvs = [s.strip() for s in sdql.split('@')]

            if '=' in cols:
                raise ValueError(f'columns cannot contain key-value pairs, only keys: {cols}')

            cols = [s.strip() for s in cols.split(',')]

            for col in cols:
                if col not in SDQL_PARAMS:
                    raise ValueError((f'{key} is not a valid parameter. '                            
                                       'to see a list of valid parameters view SDB.SDQL_PARAMS')) 

            kvs = [s.strip() for s in kvs.split(' and ')]
        else:
            kvs = [s.strip() for s in sdql.split(' and ')]

        for kv in kvs:
            try:
                key, value = kv.split('=')
            except ValueError:
                raise ValueError((f'malformed key-value pair: {kv}. should be in the '
                                   'format "key=value"'))

            if key not in SDQL_PARAMS:
                raise ValueError((f'{key} is not a valid parameter. '
                                   'to see a list of valid parameters view SDB.SDQL_PARAMS'))

            if key == 'team':
                if value not in TEAM_ABBRVS.values():
                    raise ValueError((f'{value} is not a valid team abbreviation. to see a '
                                       'list of valid abbreviations, look at SDB.TEAM_ABBRVS'))

        return quote(sdql)

    def _request(self, encoded_sdql: str) -> dict:
        url = BASE_URL.format(sport=self.SPORT, api_key=self.API_KEY, sdql=encoded_sdql)

        r = requests.get(url)

        if r.status_code >= 200 and r.status_code <= 299:
            return r.json()

        r.raise_for_status()

        return None
