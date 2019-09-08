import json
from urllib.parse import quote

import requests


class SDB:
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

    with open('team-abbrvs.json', 'r') as f:
        TEAM_ABBRVS = json.load(f)

    def __init__(self, sport: str, use_api: bool = True, api_key: str = 'guest') -> None:
        supported = ('ncaafb',)

        if sport not in supported:
            raise ValueError(f'the only supported sports are currently: {supported}')

        self.SPORT = sport
        self.USE_API = use_api
        self.API_KEY = api_key

        if self.USE_API:
            self.BASE_URL = 'http://api.sportsdatabase.com/{sport}/query.json?sdql={sdql}&output=json&api_key={api_key}'
        else:
            self.BASE_URL = 'http://sportsdatabase.com/{sport}/query?output=default&sdql={sdql}'

    def query(self, sdql: str) -> dict:
        encoded = self._verify_and_encode_sdql(sdql)

        return self._request(encoded)

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
                if ':' in col:
                    try:
                        ref, col = col.split(':')
                    except ValueError:
                        raise ValueError(f'malformed reference:parameter pair: {ref}:{col}')

                    if ref not in 'topPnN':
                        raise ValueError(f'invalid game reference: {ref}:{col}')

                if col not in SDB.SDQL_PARAMS:
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

            if ':' in key:
                try:
                    ref, key = key.split(':')
                except ValueError:
                    raise ValueError(f'malformed reference:parameter pair: {ref}:{key}')

                if ref not in 'topPnN':
                    raise ValueError(f'invalid game reference: {ref}:{col}')

            if key not in SDB.SDQL_PARAMS:
                raise ValueError((f'{key} is not a valid parameter. '
                                   'to see a list of valid parameters view SDB.SDQL_PARAMS'))

            if key == 'team':
                if value not in SDB.TEAM_ABBRVS.values():
                    raise ValueError((f'{value} is not a valid team abbreviation. to see a '
                                       'list of valid abbreviations, look at SDB.TEAM_ABBRVS'))

        return quote(sdql)

    def _request(self, encoded_sdql: str) -> dict:
        if self.USE_API:
            url = self.BASE_URL.format(sport=self.SPORT, api_key=self.API_KEY, sdql=encoded_sdql)
        else:
            url = self.BASE_URL.format(sport=self.SPORT, sdql=encoded_sdql)

        r = requests.get(url)

        data = None

        if r.status_code >= 200 and r.status_code <= 299:
            if self.USE_API:
                data = r.json()
            else:
                # TODO: get data from html table

        r.raise_for_status()

        return data
