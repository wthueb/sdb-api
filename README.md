# sdb-api
Python API for SportsDatabase.com

### usage:
```
sdb = SDB('ncaafb', use_api=True, api_key='guest', debug=False)
betting_data, game_data = sdb.query('team=ALA and o:team=CLEM')

# betting_data = {'SU': '3-2-0 (3.00, 60.0%)', 'ATS': '2-3-0 (-0.40, 40.0%) avg: -3.4', 'O/U': '3-2-0 (6.60, 60.0%) avg: 50.4'}
# game_data = [
#     {'Date': 'Aug 30, 2008', 'Link': 'box', 'Day': 'Saturday', 'Week': '1', 'Season': '2008', 'Team': 'ALA', 'Opp': 'CLEM', 'Site': 'neutral', 'Q1': '0-13', 'Q2': '3-10', 'Q3': '7-8', 'Q4': '0-3', 'Final': '34-10', 'Line': '4.5', 'Total': '46.5', 'SUm': '24', 'ATSm': '28.5', 'OUm': '-2.5', 'DPS': '13.0', 'DPA': '-15.5', 'SUr ': 'W', 'ATSr': 'W', 'OUr': 'U', 'ot': '0'
#     {'Date': 'Jan 11, 2016', 'Link': 'box', 'Day': 'Monday', 'Week': '19', 'Season': '2015', 'Team': 'ALA', 'Opp': 'CLEM', 'Site': 'neutral', 'Q1': '7-14', 'Q2': '7-0', 'Q3': '7-10', 'Q4': '24-16', 'Final': '45-40', 'Line': '-6.5', 'Total': '50.5', 'SUm': '5', 'ATSm': '-1.5', 'OUm': '34.5', 'DPS': '16.5', 'DPA': '18.0', 'SUr ': 'W', 'ATSr': 'L', 'OUr': 'O', 'ot': '0'
#     {'Date': 'Jan 09, 2017', 'Link': 'box', 'Day': 'Monday', 'Week': '19', 'Season': '2016', 'Team': 'ALA', 'Opp': 'CLEM', 'Site': 'neutral', 'Q1': '7-0', 'Q2': '7-7', 'Q3': '10-7', 'Q4': '7-21', 'Final': '31-35', 'Line': '-6.5', 'Total': '51.5', 'SUm': '-4', 'ATSm': '-10.5', 'OUm': '14.5', 'DPS': '2.0', 'DPA': '12.5', 'SUr ': 'L', 'ATSr': 'L', 'OUr': 'O', 'ot': '0'
#     {'Date': 'Jan 01, 2018', 'Link': 'box', 'Day': 'Monday', 'Week': '18', 'Season': '2017', 'Team': 'ALA', 'Opp': 'CLEM', 'Site': 'neutral', 'Q1': '10-0', 'Q2': '0-3', 'Q3': '14-3', 'Q4': '0-0', 'Final': '24-6', 'Line': '-3.0', 'Total': '46.5', 'SUm': '18', 'ATSm': '15', 'OUm': '-16.5', 'DPS': '-0.8', 'DPA': '-15.8', 'SUr ': 'W', 'ATSr': 'W', 'OUr': 'U', 'ot': '0'
#     {'Date': 'Jan 07, 2019', 'Link': 'box', 'Day': 'Monday', 'Week': '19', 'Season': '2018', 'Team': 'ALA', 'Opp': 'CLEM', 'Site': 'neutral', 'Q1': '13-14', 'Q2': '3-17', 'Q3': '0-13', 'Q4': '0-0', 'Final': '16-44', 'Line': '-5.5', 'Total': '57.0', 'SUm': '-28', 'ATSm': '-33.5', 'OUm': '3', 'DPS': '-15.2', 'DPA': '18.2', 'SUr ': 'L', 'ATSr': 'L', 'OUr': 'O', 'ot': '0'}
# ]
```
