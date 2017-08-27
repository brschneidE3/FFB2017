
import create_players
import LeagueClass
import Draft

################### Input parameters ###################
pick_no = 1

# Track who has been drafted
my_drafted_player_indices = \
    [165, 211, 39, 84, 54, 208, 53, 36, 119, 246]
other_drafted_player_indices = \
    [98, 213, 245, 13, 59, 12, 247, 237, 216, 111, 32, 104, 219,
     72, 166, 160, 125, 11, 207, 46, 30, 22, 47, 24, 34, 121,
     6, 159, 20, 29, 152, 190, 148, 202, 35, 231, 133, 10, 8,
     144, 16, 145, 60, 87, 102, 78, 214, 3, 129, 92, 169, 91,
     114, 31, 55, 48, 79, 158, 210, 76, 95, 234, 109, 206, 218,
     127, 0, 101, 235, 26, 75, 61, 5, 96, 179, 156, 194,
     15, 82, 184, 185, 49, 14, 149, 70, 74, 135, 77, 27, 19,
     188, 67, 126, 230, 93, 242, 204, 58, 196, 90, 178, 168,
     198, 183, 80, 45, 97, 94, 18, 44, 192, 244, 68, 21, 220, 23,
     238, 37, 38,]
untracked_drafted = 11
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
