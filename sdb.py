import json
from urllib.parse import quote

from fake_useragent import UserAgent
import lxml.etree
import lxml.html
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

            self.USER_AGENT = UserAgent()

    def query(self, sdql: str) -> (dict, list):
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

    def _request(self, encoded_sdql: str) -> (dict, list):
        if self.USE_API:
            url = self.BASE_URL.format(sport=self.SPORT, api_key=self.API_KEY, sdql=encoded_sdql)

            r = requests.get(url)
        else:
            url = self.BASE_URL.format(sport=self.SPORT, sdql=encoded_sdql)

            headers = {'user-agent': self.USER_AGENT.chrome}

            r = requests.get(url, headers=headers)

        betting_data = None
        game_data = None

        if r.status_code >= 200 and r.status_code <= 299:
            if self.USE_API:
                # TODO: format json into betting_data and game_data
                pass
            else:
                # TODO: get betting data table
                root = lxml.html.fromstring(r.text)

                betting_table = root.xpath('/html/body/table')[2]
                betting_table = betting_table.xpath('./tr')[1]
                betting_table = betting_table.xpath('.//table')[0]

                betting_data = {}

                for row in betting_table.xpath('./tr'):
                    # [:-1] to get rid of colon
                    header = row.xpath('./th')[0].text_content().strip()[:-1]

                    table_data = row.xpath('./td')

                    if len(table_data) == 2:
                        betting_data[header] = table_data[0].text_content().strip()
                    else:
                        outcome = table_data[0].text_content().strip()
                        avg = table_data[1].text_content().strip().split(':')[-1].strip()

                        betting_data[header] = f'{outcome} avg: {avg}'

                game_table = root.xpath('//table[@id="DT_Table"]')[0]

                headers = [h.text_content() for h in game_table.xpath('.//thead/tr/th')]

                #game_data = [{headers[i]: c.text_content().strip() for i, c in enumerate(r.xpath('.//td'))} for r in game_table.xpath('.//tr')][1:]

                game_data = []

                # [1:] because you want to skip the header row
                for row in game_table.xpath('.//tr')[1:]:
                    box_score = {}

                    for i, col in enumerate(row.xpath('.//td')):
                        box_score[headers[i]] = col.text_content().strip()

                    game_data.append(box_score)

        r.raise_for_status()

        return betting_data, game_data


if __name__ == '__main__':
    sdb = SDB('ncaafb', use_api=False)

    betting, game = sdb.query('team=ALA and o:team=CLEM')

    print(betting)
    print(game)
