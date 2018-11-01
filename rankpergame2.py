"""
This script scrapes data from ESPN fantasy bball league and calculates points
per game.

Install all python dependencies (i.e selenium)

Need to install geckodriver from here: https://github.com/mozilla/geckodriver/releases
Extract file and move: sudo mv geckodriver /usr/local/bin

Be prepared to login to espn every time you run this script
"""


# dependencies
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

url = 'http://fantasy.espn.com/basketball/league/standings?leagueId=82026010'
driver = webdriver.Firefox()
driver.get(url)

### Pause and make sure you are signed in 

html = driver.page_source
soup = BeautifulSoup(html, "lxml")

#### These next few lines write the html to a file, which can be helpful
# import sys
# sys.stdout = open('div2.txt', 'w')
# soup

# scrape team names
teams = soup.find_all('span', class_ = "teamName truncate")
team_names = []
for team in teams:
    name = team['title']
    team_names.append(name)

team_names = team_names[0:10]

stats = soup.find_all('div', class_='jsx-2810852873 table--cell stat-value tar')
stats_clean = [str(i).split(">")[1].split("<")[0] for i in stats]





###### Old code
""" def get_stats(stat_name):
    """function to scrape stats"""
    stats = soup.find_all('td', class_=stat_name)
    lis = []
    for stat in stats:
        n = float(stat.find(text=True))
        lis.append(n)
    return lis

# scrape stats
fg = get_stats('precise sortableStat19')  # field goal percentages
ft = get_stats('precise sortableStat20')  # free throw percentages
tpm = get_stats('precise sortableStat17')  # three pointers made
reb = get_stats('precise sortableStat6')  # rebounds
ast = get_stats('precise sortableStat3')  # assists
stl = get_stats('precise sortableStat2')  # steals
blk = get_stats('precise sortableStat1')  # blocks
pts = get_stats('precise sortableStat0')  # points
gp = get_stats('sortableGP')  # games played
moves = get_stats('sortableMoves')  # number of moves

# create dataframe
dic = {'FG': fg, 'FT': ft, '3PM': tpm, 'REB': reb, 'AST': ast, 'STL': stl,
       'BLK': blk, 'PTS': pts, 'GP': gp, 'MOVES': moves}
df = pd.DataFrame(dic, index=team_names)

# calculate stats per games played
df_new = df.div(df.GP, axis='index')
df_new.FG = df.FG
df_new.FT = df.FT
df_new.GP = df.GP
df_new.MOVES = df.MOVES

# rescore and rank
df_ranks = df_new.rank(axis=0, method='average')
del df_ranks['MOVES']
del df_ranks['GP']
df_ranks['TOTAL'] = df_ranks.sum(axis=1)

print df_ranks.sort_values('TOTAL', ascending=False) """
