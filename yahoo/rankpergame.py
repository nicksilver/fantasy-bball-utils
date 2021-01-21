from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import pandas as pd
import sys

oauth = OAuth2(None, None, from_file='oauth2.json')

if not oauth.token_is_valid():
    oauth.refresh_access_token()


def get_response(url, payload={'format': 'json'}):
    return oauth.session.get(url, params=payload)


def get_raw_stats(url):
    team_names = [str(i) for i in list(range(10))]
    response = get_response(url)
    teams = response.json()['fantasy_content']['league'][1]['standings'][0]['teams']
    raw_stats = pd.DataFrame()
    for team in team_names:
        stats = teams[team]['team'][1]['team_stats']['stats']
        nm = teams[team]['team'][0][2]['name']
        col_names = []
        values = []
        for stat in stats:
            col_names.append(str(stat['stat']['stat_id']))
            values.append(stat['stat']['value'])
        df = pd.DataFrame([values], columns=col_names, index=[nm])
        raw_stats = raw_stats.append(df)
    return raw_stats


def get_stat_key(url):
    response = get_response(url)
    stat_names = response.json()['fantasy_content']['league'][1]['settings'][0]['stat_categories']['stats']
    stat_dict = {}
    for sn in stat_names:
        if sn['stat']['enabled'] == '1':
            stat_dict[str(sn['stat']['stat_id'])] = sn['stat']['display_name']
    return stat_dict


def process_raw_stats(url_league, url_settings):
    raw_stats = get_raw_stats(url_league)
    stat_dict = get_stat_key(url_settings)
    raw_stats = raw_stats.rename(columns=stat_dict)
    raw_stats = raw_stats.rename(columns={'0': 'GP'})
    raw_stats = raw_stats.drop(columns=['FGM/A', 'FTM/A'])
    raw_stats = raw_stats.apply(pd.to_numeric)
    return raw_stats


def rankpergame(url_league, url_settings):
    proc_stats = process_raw_stats(url_league, url_settings)

    # Use the drop setting if people do not seem to be playing games
    if (len(sys.argv) > 1) and (sys.argv[1] == "--drop"):
        keep_bool = proc_stats.GP/max(proc_stats.GP) > 0.70
        proc_stats = proc_stats.loc[keep_bool]

    norm_stats = proc_stats.div(proc_stats.GP, axis=0).drop(columns=['GP'])
    norm_stats['FG%'] = proc_stats['FG%']
    norm_stats['FT%'] = proc_stats['FT%']
    df_ranks = norm_stats.rank(axis=0, method='average')
    df_ranks['TOTAL'] = df_ranks.sum(axis=1)
    norm_stats['TOTAL'] = df_ranks['TOTAL']
    print(norm_stats.sort_values('TOTAL', ascending=False))
    print(df_ranks.sort_values('TOTAL', ascending=False))


if __name__ == '__main__':
    gm = yfa.Game(oauth, 'nba')
    lid = gm.league_ids(year=2020)
    url_league = 'https://fantasysports.yahooapis.com/fantasy/v2/league/' + lid[0] + '/standings'
    url_settings = 'https://fantasysports.yahooapis.com/fantasy/v2/league/' + lid[0] + '/settings'
    rankpergame(url_league, url_settings)
