import csv
import PlayerClass
from coopr import pyomo

def get_team_picks(num_teams, pick_no, num_rounds):
    picks = []
    for round in range(1, num_rounds + 1):
        # Odd round
        if round % 2 == 1:
            round_pick = pick_no
        # Even round
        else:
            round_pick = num_teams - pick_no + 1
        overall_pick = round_pick + num_teams*(round - 1)
        picks.append(overall_pick)
    return picks

def create_players():
    players = {}
    with open('points.csv', 'rb') as csv_file:
        reader = csv.reader(csv_file)
        first_row = True

        for row in reader:
            if first_row:
                first_row = False
                pass
            else:
                player_id = row[0].replace('\xa0', ';')
                points = {i-1: float(row[i]) for i in range(2, 18)}

                player = PlayerClass.Player(player_id)
                player.add_points(points)
                players[player_id] = player
    return players


def add_avg_picks(players):
    with open('avg pick.csv', 'rb') as csv_file:
        reader = csv.reader(csv_file)
        first_row = True

        for row in reader:
            if first_row:
                first_row = False
                pass
            else:
                player_id, avg_pick = row[0].replace('\xa0', ';'), float(row[1])
                player = players[player_id]
                player.add_avg_pick(avg_pick)

def get_players_to_draft(solved_opt):
    ps_to_draft = []
    for player in solved_opt.avail_players:
        if pyomo.value(solved_opt.used[player]):
            ps_to_draft.append(player)
    return ps_to_draft

def print_players_to_draft(solved_opt, prob_avail):
    ps_to_draft = get_players_to_draft(solved_opt)

    print '####### PLAYERS TO DRAFT #######'
    for player in ps_to_draft:
        print '\t %s, p=%s' % (player.id, str(prob_avail[player])[:5])

def get_prob_avail_after(players_drafted_between_picks, player_avg_pick, num_drafted, width=1.5):

    threshold = width*players_drafted_between_picks
    avg_pick_upper_bound = num_drafted + threshold
    avg_pick_lower_bound = num_drafted - threshold

    if avg_pick_lower_bound == avg_pick_upper_bound:
        return 1

    # If we probably have another pick before player gets taken
    elif player_avg_pick > avg_pick_upper_bound:
        return 1

    # Elif we probably don't have another draft pick before player gets taken
    elif player_avg_pick < avg_pick_lower_bound:
        return 0

    else:
        p_avail = (player_avg_pick - avg_pick_lower_bound)/(avg_pick_upper_bound - avg_pick_lower_bound)
        if p_avail > 1 or p_avail < 0:
            print 'Error calculating p_avail'
            exit()
        return p_avail