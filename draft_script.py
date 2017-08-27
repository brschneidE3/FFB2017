
import create_players
import LeagueClass
import Draft

################### Input parameters ###################
pick_no = 1

# Track who has been drafted
my_drafted_player_indices = \
    []
other_drafted_player_indices = \
    []
untracked_drafted = 0
# List them here:
########################################################

num_teams = 14
num_rounds = 17 + 1

# Create player universe
import helpers
players = create_players.create_players()
helpers.calc_avg_pick(players)
helpers.add_avg_picks(players)
create_players.save_players(players)

# Load player universe into league
players = create_players.load_players()
league = LeagueClass.League(players)
league.print_num_pos()
print '...players created...'

my_drafted_players = [players.values()[i] for i in my_drafted_player_indices]
other_drafted_players = [players.values()[i] for i in other_drafted_player_indices]

# List available players
available_players = Draft.get_available_players(players, my_drafted_players, other_drafted_players, printon=True)
print '...available players collected...'

# Calculate P(drafted) for every available player
prob_avail_after_dict, draft_risks = \
    Draft.get_prob_avail_after(available_players,
                               my_drafted_players,
                               other_drafted_players,
                               pick_no, num_rounds, num_teams, untracked_players_drafted=untracked_drafted)
print '...probability of being drafted calculated...'
print '...evaluating %s players potentially drafted...' % draft_risks
