__author__ = 'brendan'

import csv
from YHandler import YHandler, YQuery
handler = YHandler()
query = YQuery(handler, 'nfl')
league_no = "427623"

stat_dictionary = query.stat_categories
game_info = query.get_games_info()
leagues_to_date = query.get_user_leagues()

# week9_stats = query.get_player_week_stats(id_no, '9')
#
# query_keys = query.__dict__
# for key in query_keys['stat_categories']:
#     print key, query_keys['stat_categories'][key]['name']

# resp = query.query_player(id_no, 'stats')
# print query.get_player_stats(resp)


# Draft results
# resp = query.query_league(league_no, 'draftresults')
# pick_no = 0
# for pick in resp.iter_select('.//yh:draft_results/yh:draft_result', query.ns):
#     player_id = pick.select_one('./yh:player_key', query.ns).text
#     pick_no += 1
#     draft_pick = query.player_by_key(league_no, player_id)[0]
#     player_name = draft_pick['name']
#     print '%s: %s' % (pick_no, player_name)

# player_keys = query.all_player_ids(league_no)
# for key in player_keys:
#     player = query.player_by_key(league_no, key)[0]
#     print player['name']

# querystring = 'leagues;league_keys=238.l.627060/draftresults'
# query = handler.api_req(querystring)
# print query

ids = query.all_player_ids(league_no)
with open('player_ids.csv', 'wb') as csvfile:
    rowwriter = csv.writer(csvfile)
    rowwriter.writerow(['index', 'player_id'])
    for i in range(len(ids)):
        rowwriter.writerow([i, ids[i]])