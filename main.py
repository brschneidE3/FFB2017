import helpers
import LeagueClass
import time

if __name__ == '__main__':
    import operator
    import tabulate

    from multiprocessing import Pool

################### Input parameters ###################
# set draft pick
pick_no = 1
num_teams = 14
num_rounds = 17 + 1

# Track players drafted so far -- ONLY THING THAT SHOULD BE UPDATED
my_drafted_players = \
    []
other_drafted_players = \
    []
    # [1, 2, 3, 4,5, 6, ]
########################################################

# Load projection data
players = helpers.create_players()
# helpers.calc_avg_pick(players)
# exit()
helpers.add_avg_picks(players)
available_players = [key for key in players.keys() if 'Untracked' not in key]
available_players += [key for key in players.keys() if 'Untracked' in key]

if __name__ == '__main__':
    # Print indices of players available to start
    for i in range(len(available_players)):
        player_id = available_players[i]
        print '%s) %s' % (i, player_id)
    print '\n'

# Create league
league = LeagueClass.League(num_teams=num_teams, num_rounds=num_rounds, players=players)

# Convert indices to ids
team_playerids = [available_players[i] for i in my_drafted_players]
other_playerids = [available_players[i] for i in other_drafted_players]
drafted_players = team_playerids + other_playerids

# Calculate what next pick would be overall
num_drafted = len(drafted_players)

# Figure out next team pick
team_picks = helpers.get_team_picks(num_teams=num_teams, pick_no=pick_no, num_rounds=num_rounds)
remaining_team_picks = [element for element in team_picks if element > (num_drafted + 1)]  # assumes next pick is mine
next_team_pick = remaining_team_picks[0]
players_drafted_between_picks = next_team_pick - num_drafted - 2

# Fixed bookend scenario
if players_drafted_between_picks == 0:
    players_drafted_between_picks = num_teams*2 - 2
    next_team_pick = remaining_team_picks[1]

# Remove drafted players from available
for player_id in drafted_players:
    available_players.remove(player_id)

# Calculate prob_avail_after for each avail player
prob_avail_after = {}
for player_id in available_players:
    player = players[player_id]
    player_avg_pick = player.avg_pick
    p_avail = helpers.get_prob_avail_after(players_drafted_between_picks, player_avg_pick, next_team_pick,
                                           width=0.)
    prob_avail_after[player] = p_avail

def evaluate_next_pick(i, print_team=False):
    player_id = available_players[i]
    player = players[player_id]

    if prob_avail_after[player] < 1.:
        # Add player to team, and remove from available pool
        team_with_player = team_playerids + [player_id]
        avail_players_without_player = \
            [p for p in available_players if p != player_id and 'Untracked' not in p]

        # Create model
        model_w_player = \
            league.create_optimal_model(team_with_player,
                                        avail_players_without_player,
                                        prob_avail_after)

        # Solve model
        solved_opt_w_player = league.solve_optimal_model(model_w_player, printon=True)

        # Get team projection
        value_w_player = league.get_optimal_points(solved_opt_w_player)
        value = value_w_player

        if print_team:
            league.print_position_weeks_by_undrafted_player(solved_opt_w_player)
    else:
        value = 0

    return value

if __name__ == '__main__':

    # Break up optimization across 8 processors
    parallel_start = time.time()
    pool = Pool(processes=8)

    player_is = [113, 187, 197]
    # player_is = range(len(available_players))

    values = list(pool.imap(evaluate_next_pick, player_is))
    pool.close()
    pool.join()

    # Save results
    parallel_results = {}
    for i in range(len(player_is)):
        player_i = player_is[i]
        player_id = available_players[player_i]
        value = values[i]
        parallel_results[player_id] = value

    # Find base solution
    min_nonzero_value = min(result for result in parallel_results.values() if result > 0)
    min_nonzero_index = values.index(min_nonzero_value)
    min_nonzero_player = available_players[min_nonzero_index]

    # Print results
    sorted_values_by_player = sorted(parallel_results.items(), key=operator.itemgetter(1), reverse=True)
    value_table = []
    for i in range(len(sorted_values_by_player)):
        player_id, value = sorted_values_by_player[i]

        if value > 0:
            try:
                value_table.append([player_id,
                                    value,
                                    value - sorted_values_by_player[i + 1][1],
                                    sorted_values_by_player[0][1] - value])
            except IndexError:
                value_table.append([player_id, value, 'N/A'])

    print tabulate.tabulate(value_table, ['Player', 'Value', 'd_Value', 'cum_Value']), '\n'

    # Report on solve time
    parallel_end = time.time()
    elapsed = parallel_end - parallel_start
    print '\noptimal draft solve time: %s' % elapsed

    # Print base solution
    print '\n######################################## SLEEPER ROSTER ########################################'
    model_result = evaluate_next_pick(min_nonzero_index, print_team=True)
    print 'next pick: %s' % (num_drafted + 1)
