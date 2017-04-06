__author__ = 'brendan'

import csv

# Create querying infrastructure
from YHandler import YHandler, YQuery
handler = YHandler()
query = YQuery(handler, 'nfl')
league_no = "427623"

# Look up leagues so far
league_keys = {}  # Gives season given league
league_seasons = {}  # Gives leagues given season
leagues_to_date = query.get_user_leagues()

for league in leagues_to_date:
    league_id = league['id']
    league_year = league['season']

    if int(league_year) >= 2014:
        league_keys[league_id] = league_year
        league_seasons[league_year] = league_id

all_player_keys = [['League', 'Year', 'PlayerID']]
all_draft_picks = [['League', 'Year', 'Pick', 'Team', 'PlayerID']]

# Iterate through each league and get all players in that league plus
for league_key in league_keys.keys():
    season = league_keys[league_key]
    player_ids = query.all_player_keys(league_key)
    for key in player_ids:
        all_player_keys.append([league_key, season, key])

    draft_info = query.query_league(league_key, 'draftresults')
    for pick in draft_info.iter_select('.//yh:draft_results/yh:draft_result', query.ns):
        player_id = pick.select_one('./yh:player_key', query.ns).text
        pick_number = pick.select_one('./yh:pick', query.ns).text
        team = pick.select_one('./yh:team_key', query.ns).text

        all_draft_picks.append([league_key, season, pick_number, team, player_id])

with open('player_ids.csv', 'wb') as csvfile:
    rowwriter = csv.writer(csvfile)
    for i in range(len(all_player_keys)):
        rowwriter.writerow(all_player_keys[i])

with open('draft_results.csv', 'wb') as csvfile:
    rowwriter = csv.writer(csvfile)
    for i in range(len(all_draft_picks)):
        rowwriter.writerow(all_draft_picks[i])