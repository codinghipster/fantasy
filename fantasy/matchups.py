import logging

from bs4 import BeautifulSoup
import requests

logger = logging.getLogger(__name__)

attr_map = {
    'Yet to Play:': 'yet_to_play',
    'In Play:': 'playing',
    'Mins Left:': 'minutes_left',
    'Proj Total:': 'projection',
    'Line:': 'line',
    'Top Scorer:': 'top_scorer',
}


url_base = "http://games.espn.go.com/ffl"


def scrape(league_id, year):
    url = "{}/scoreboard?leagueId={}&seasonId={}".format(
        url_base, league_id, year)
    content = requests.get(url).content
    soup = BeautifulSoup(content)
    return _get_matchups(soup)


def _from_scoring_details(headers, info):
    ret = {}
    for header, data in zip(headers, info):
        ret[attr_map[header.text]] = data.text
    return ret


def _get_matchups(soup):
    matchups = []
    for table in soup.find_all('table', 'matchup'):
        rows = table.find_all('tr')
        matchup = rows[2].find('table').find_all('td')

        teams = []
        for count, team in enumerate(rows[0:2]):
            name = team.find('a').text
            owners = team.find('span', 'owners').text
            score = team.find('td', 'score').text

            data = matchup[count*3:(count+1)*3]
            abbreviation = data[0].text
            team = _from_scoring_details(data[1], data[2])
            team.update({
                'name': name,
                'owners': owners,
                'score': score,
                'abbreviation': abbreviation,
            })
            teams.append(team)
        matchups.append(teams)

    return matchups
