from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import pandas as pd
import numpy as np

oauth = OAuth2(None, None, from_file='oauth2.json')

if not oauth.token_is_valid():
    oauth.refresh_access_token()

gm = yfa.Game(oauth, 'nba')
lid = gm.league_ids(year=2019)
lg = gm.to_league(lid[0])
lg.stat_categories()

url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/' + lid[0] + '/standings'
payload = {'format': 'json'}
response = oauth.session.get(url, params=payload)

# Get league stats
team_names = [str(i) for i in list(range(10))]
teams = response.json()['fantasy_content']['league'][1]['standings'][0]['teams']
league_stats = pd.DataFrame()
for team in team_names:
    stats = teams[team]['team'][1]['team_stats']['stats']
    nm = teams[team]['team'][0][2]['name']
    col_names = []
    values = []
    for stat in stats:
        col_names.append(str(stat['stat']['stat_id']))
        values.append(stat['stat']['value'])
    df = pd.DataFrame([values], columns=col_names, index=[nm])
    league_stats = league_stats.append(df)

# Get stat names
url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/' + lid[0] + '/settings'
payload = {'format': 'json'}
response = oauth.session.get(url, params=payload)
stat_names = response.json()['fantasy_content']['league'][1]['settings'][0]['stat_categories']['stats']
stat_dict = {}
for sn in stat_names:
    if sn['stat']['enabled'] == '1':
        stat_dict[str(sn['stat']['stat_id'])] = sn['stat']['display_name']

league_stats = league_stats.rename(columns=stat_dict)
league_stats = league_stats.rename(columns={'0': 'GP'})
league_stats = league_stats.drop(columns=['FGM/A', 'FTM/A'])
league_stats = league_stats.apply(pd.to_numeric)

norm_stats = league_stats.div(league_stats.GP, axis=0).drop(columns=['GP'])
norm_stats['FG%'] = league_stats['FG%']
norm_stats['FT%'] = league_stats['FT%']
df_ranks = norm_stats.rank(axis=0, method='average')

df_ranks['TOTAL'] = df_ranks.sum(axis=1)
print(df_ranks.sort_values('TOTAL', ascending=False))