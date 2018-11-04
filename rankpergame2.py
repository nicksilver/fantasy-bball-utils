"""
This script scrapes data from ESPN fantasy bball league and calculates points
per game.

Install all python dependencies (i.e selenium)

Need to install geckodriver from here: https://github.com/mozilla/geckodriver/releases
Extract file and move: sudo mv geckodriver /usr/local/bin

To run script:
    python rankpergame.py "username" "password"
"""

# dependencies
import sys
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.by import By

# Open website, automatically login, and scrape html
url = 'http://fantasy.espn.com/basketball/league/standings?leagueId=82026010'
driver = webdriver.Firefox()
driver.get(url)
WebDriverWait(driver,1000).until(EC.presence_of_all_elements_located((By.XPATH,"(//iframe)")))
frms = driver.find_elements_by_xpath("(//iframe)")
driver.switch_to.frame(frms[0])
time.sleep(2)
driver.find_element_by_xpath("(//input)[1]").send_keys(sys.argv[1])
driver.find_element_by_xpath("(//input)[2]").send_keys(sys.argv[2])
driver.find_element_by_xpath("//button").click()
driver.switch_to.default_content()
time.sleep(4)
html = driver.page_source
soup = BeautifulSoup(html, "lxml")

# Soup functions
def _scrape_names(soup):
    """Returns list of team names with exception of user"""
    teams = soup.find_all('span', class_ = "teamName truncate")
    team_names = []
    for team in teams:
        name = team['title']
        team_names.append(name)
    team_names = team_names[0:10]
    return team_names

def _scrape_user_name(soup):
    """Returns user team name"""
    my_name = soup.find_all('span', class_= "Nav__Text clr-gray-04 n8 pl3 truncate")
    my_name_clean = str(my_name).split(">")[1].split("<")[0]
    return my_name_clean

def _stats_df(soup):
    """Returns dataframe with out user stats"""
    team_names = _scrape_names(soup)
    my_name = _scrape_user_name(soup)
    stats = soup.find_all('div', class_='jsx-2810852873 table--cell stat-value tar')
    stats_clean = [str(i).split(">")[1].split("<")[0] for i in stats]
    gp = stats_clean[-9:]
    stat_names = ["FG%", "FT%", "3PM", "REB", "AST", "STL", "BLK", "PTS"]
    ind = team_names
    ind.remove(my_name)
    df_stats = pd.DataFrame(np.asarray(stats_clean[:-9]).reshape([9, 8]),
                            columns=stat_names, index=ind)
    df_stats['GP'] = gp
    return df_stats

def _my_stats_df(soup):
    """Returns user stats without index and column names"""
    my_stats = soup.find_all('div', class_="jsx-2810852873 table--cell stat-value tar fw-bold")
    my_stats_clean = [str(i).split(">")[1].split("<")[0] for i in my_stats]
    my_df = pd.DataFrame([my_stats_clean])
    return my_df

def _create_full_stats_df(soup):
    """Returns full stats dataframe"""
    my_name = _scrape_user_name(soup)
    df_stats = _stats_df(soup)
    my_df = _my_stats_df(soup)
    my_df.columns = df_stats.columns
    my_df.index = [my_name]
    df_stats = df_stats.append(my_df)
    return df_stats.astype(float)

def _normalize_stats(soup):
    """Returns stats dataframe normalized by games played"""
    df_stats = _create_full_stats_df(soup)
    df_new = df_stats.div(df_stats.GP, axis='index')
    df_new['FG%'] = df_stats['FG%']
    df_new['FT%'] = df_stats['FT%']
    df_new['GP'] = df_stats['GP']
    return df_new

def rankpergame(soup):
    """Main function the returns dataframe ranked per game"""
    norm_stats = _normalize_stats(soup)
    df_ranks = norm_stats.rank(axis=0, method='average')
    del df_ranks['GP']
    df_ranks['TOTAL'] = df_ranks.sum(axis=1)
    print df_ranks.sort_values('TOTAL', ascending=False)


if __name__ == '__main__':
    rankpergame(soup)
    driver.close()
