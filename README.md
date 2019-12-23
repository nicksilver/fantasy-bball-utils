# Fantasy Basketball Utilities

## ESPN - rankpergame_scraper
Scrapes the ESPN fantasy basketball website to calculate mid-season rankings based on the number of games played. This script worked for the 2018-2019 season. It usually needs to be updated each year. You will need to be logged into your ESPN account online for it to be able to scrape data.

The dependencies for this script are:

    - Python 2
    - pandas
    - numpy
    - requests
    - BeautifulSoup
    - selenium

## Yahoo - rankpergame
Uses the Yahoo Fantasy API to calculate mid-season rankings based on the number of games played. You need to have authentication for the Yahoo API stored in a `oauth2.json` file.

The dependencies for this script are:

    - Python 3
    - pandas
    - numpy
    - yahoo_oauth
    - yahoo_fantasy_api

### See the python yahoo_oauth documentation for more details on authentication
https://yahoo-oauth.readthedocs.io/en/latest/

