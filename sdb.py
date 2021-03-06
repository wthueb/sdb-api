import json
import logging
from urllib.parse import quote

import pandas as pd
import requests


class SDB:
    NCAAFB_PARAMS = ('ats margin', 'ats streak', 'cdivision', 'coach', 'completions',
                     'conference', 'date', 'day', 'division', 'dpa', 'dps', 'first downs',
                     'fourth downs attempted', 'fourth downs made', 'full name', 'fumbles',
                     'fumbles lost', 'game number', 'game type', 'interceptions', 'line',
                     'losses', 'margin', 'margin after the first', 'margin after the third',
                     'margin at the half', 'matchup losses', 'matchup wins', 'month',
                     'opponents', 'ou margin', 'ou streak', 'overtime', 'passes',
                     'passing yards', 'penalties', 'penalties yards', 'penalty yards',
                     'playoffs', 'points', 'quarter scores', 'rank', 'rest', 'rot', 'round',
                     'rushes', 'rushing yards', 'school', 'season', 'seed', 'site',
                     'site streak', 'start time', 'streak', 'team', 'third downs attempted',
                     'third downs made', 'time of possession', 'total', 'turnover margin',
                     'turnovers', 'week', 'wins')

    with open('team-abbrvs.json', 'r') as f:
        TEAM_ABBRVS = json.load(f)

    def __init__(self, sport: str, use_api: bool = True, api_key: str = 'guest',
                 debug: bool = False) -> None:
        self.logger = logging.getLogger('sdb-api')
        self.logger.setLevel(logging.DEBUG)

        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG if debug else logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(name)-10s %(levelname)-7s - %(message)s')
        sh.setFormatter(formatter)

        self.logger.addHandler(sh)

        # TODO: support multiple sports & variable params
        # maybe: self.PARAMS = vars(SDB)[f'{sport.upper()}_PARAMS']
        # kinda hacky though
        supported = ('ncaafb',)

        if sport not in supported:
            raise ValueError(f'the only supported sports are currently: {supported}')

        self.SPORT = sport
        self.USE_API = use_api
        self.API_KEY = api_key

        if self.USE_API:
            self.BASE_URL = ('https://api.sportsdatabase.com/'
                             '{sport}/query.json?sdql={sdql}&output=json&api_key={api_key}')
        else:
            from fake_useragent import UserAgent

            self.BASE_URL = 'https://sportsdatabase.com/{sport}/query?output=default&sdql={sdql}'

            self.USER_AGENT = UserAgent()

            self.logger.debug(f'using user agent: {self.USER_AGENT.chrome}')

        self.logger.debug(f'using base url: {self.BASE_URL}')

    def query(self, sdql: str) -> (dict, list):
        self.logger.debug(f'raw query: {sdql}')

        try:
            self._verify_sdql(sdql)
        except Exception as e:
            logging.error('there was an error verifying your sdql query:')

            raise e

        return self._request(sdql)

    def _verify_sdql(self, sdql: str) -> None:
        if not sdql:
            raise ValueError('sdql query cannot be empty')

        if '@' in sdql:
            if sdql.count('@') > 1:
                raise ValueError(f'sdql query cannot contain multiple @ symbols: {sdql}')

            params, conditions = [s.strip() for s in sdql.split('@')]

            if '=' in params:
                raise ValueError(f'params cannot contain conditions: {params}')

            params = [s.strip() for s in params.split(',')]

            for param in params:
                if ':' in param:
                    try:
                        ref, param = param.split(':')
                    except ValueError:
                        raise ValueError(f'malformed reference:parameter pair: {ref}:{param}')

                    if ref not in 'topPnNsS':
                        raise ValueError(f'invalid reference: {ref}:{param}')

                if param not in SDB.NCAAFB_PARAMS:
                    raise ValueError((f'{param} is not a valid parameter. '
                                      'to see a list of valid parameters view SDB.NCAAFB_PARAMS'))

            conditions = [s.strip() for s in conditions.split(' and ')]
        elif self.USE_API:
            raise ValueError('sdql query must include parameters if using the api')
        else:
            conditions = [s.strip() for s in sdql.split(' and ')]

        for condition in conditions:
            try:
                param, value = condition.split('=')
            except ValueError:
                raise ValueError((f'malformed param-value pair: {condition}. should be in the '
                                  'format "param=value"'))

            if ':' in param:
                try:
                    ref, param = param.split(':')
                except ValueError:
                    raise ValueError(f'malformed reference:parameter pair: {ref}:{param}')

                if ref not in 'topPnNsS':
                    raise ValueError(f'invalid reference: {ref}:{param}')

            if param not in SDB.NCAAFB_PARAMS:
                raise ValueError((f'{param} is not a valid parameter. '
                                  'to see a list of valid parameters view SDB.NCAAFB_PARAMS'))

            if param == 'team':
                if value not in SDB.TEAM_ABBRVS.keys():
                    raise ValueError((f'{value} is not a valid team abbreviation. to see a '
                                      'list of valid abbreviations, look at SDB.TEAM_ABBRVS'))

        self.logger.debug('query is valid')

    def _request(self, sdql: str) -> (dict, list):
        encoded_sdql = quote(sdql)

        headers = {}

        if self.USE_API:
            url = self.BASE_URL.format(sport=self.SPORT, api_key=self.API_KEY, sdql=encoded_sdql)
            headers = {'user-agent': 'github/wthueb/sdb-api'}
        else:
            url = self.BASE_URL.format(sport=self.SPORT, sdql=encoded_sdql)

            headers = {'user-agent': self.USER_AGENT.chrome}

        self.logger.debug(f'sending request to: {url}')

        r = requests.get(url, headers=headers, verify=not self.USE_API)

        betting_data = {}
        game_data = []

        if r.status_code >= 200 and r.status_code <= 299:
            if self.USE_API:
                json_start = r.text.find('(') + 1
                json_end = r.text.find(')')

                stripped = r.text[json_start:json_end].replace("'", '"')

                data = json.loads(stripped)

                betting_data, game_data = self._parse_json(data)
            else:
                betting_data, game_data = self._parse_webpage(r.content, '@' in sdql)
        elif r.status_code == 404:
            if self.USE_API:
                self.logger.error('https://api.sportsdatabase.com is down')
            else:
                self.logger.error('https://sportsdatabase.com is down')
        else:
            self.logger.error(f'there was an http error when making the request: {r.status_code}')

        r.raise_for_status()

        return betting_data, game_data

    def _parse_json(self, data: dict) -> (dict, pd.DataFrame):
        # TODO: api requests can't get betting data?
        data = dict(zip(data['headers'], data['groups'][0]['columns']))

        df = pd.DataFrame.from_dict(data)

        return {}, df

    def _parse_webpage(self, html_text: str, custom_headers: bool) -> (dict, pd.DataFrame):
        dfs = pd.read_html(html_text)

        # TODO: this could break very easily, perhaps dynamically figuring out which
        # index the tables are on would be a better soluton
        betting_data = {}

        if not custom_headers:
            betting_df = dfs[3]

            betting_data['SU'] = betting_df.loc[0][1]

            ats = ''

            for elem in betting_df.loc[1][1:]:
                ats += elem + ' '

            betting_data['ATS'] = ats[:-1]

            ou = ''

            for elem in betting_df.loc[2][1:]:
                ou += elem + ' '

            betting_data['O/U'] = ou[:-1]

            game_data = dfs[5]
        else:
            game_data = dfs[3]

        return betting_data, game_data
