
import helpers

def get_available_players(players, my_drafted_players, other_drafted_players, printon):
    """
    Prints a list of undrafted players by their index in players.values()
    """
    available_players = []

    for i in range(len(players)):
        player = players.values()[i]

        if 'Untracked' not in player.id:
            if player not in my_drafted_players:
                if player not in other_drafted_players:

                    if printon:
                        print '%s) %s' % (i, player.id)

                    available_players.append(player)

    return available_players

def get_num_drafted(my_drafted_players, other_drafted_players, untracked_players_drafted):

    return len(my_drafted_players) + len(other_drafted_players) + untracked_players_drafted

def get_team_picks(pick_no, num_rounds, num_teams):

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

def get_remaining_picks(my_drafted_players, other_drafted_players, pick_no, num_rounds, num_teams, untracked_players_drafted):

    picks = get_team_picks(pick_no, num_rounds, num_teams)
    num_drafted = get_num_drafted(my_drafted_players, other_drafted_players, untracked_players_drafted)

    remaining_picks = [pick for pick in picks if pick > (num_drafted + 1)]

    return remaining_picks


def get_players_between_picks(my_drafted_players, other_drafted_players, pick_no, num_rounds, num_teams, untracked_players_drafted):

    remaining_picks = get_remaining_picks(my_drafted_players, other_drafted_players, pick_no, num_rounds, num_teams, untracked_players_drafted)

    next_team_pick = remaining_picks[0]
    num_drafted = get_num_drafted(my_drafted_players, other_drafted_players, untracked_players_drafted)

    players_drafted_between_picks = next_team_pick - num_drafted - 2

    if players_drafted_between_picks == 0:
        players_drafted_between_picks = num_teams*2 - 2
        next_team_pick = remaining_picks[1]

    return players_drafted_between_picks, next_team_pick

def get_prob_avail_after(available_players, my_drafted_players, other_drafted_players, pick_no, num_rounds, num_teams, untracked_players_drafted):

    prob_avail_after = {}
    draft_risks = 0

    players_drafted_between_picks, next_team_pick = \
        get_players_between_picks(my_drafted_players, other_drafted_players, pick_no, num_rounds, num_teams, untracked_players_drafted)

    sorted_avg_picks = sorted([player.avg_pick for player in available_players])
    max_pick_to_eval = sorted_avg_picks[players_drafted_between_picks + 2]

    for player in available_players:
        avg_pick = player.avg_pick

        if avg_pick <= max_pick_to_eval:
            p_avail = helpers.get_prob_avail_after(players_drafted_between_picks,
                                                   avg_pick,
                                                   next_team_pick,
                                                   width=0.0)
            prob_avail_after[player] = p_avail

            if prob_avail_after[player] < 1:
                draft_risks += 1

        else:
            prob_avail_after[player] = 1


    return prob_avail_after, draft_risks