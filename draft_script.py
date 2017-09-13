
import create_players
import LeagueClass
import Draft

################### Input parameters ###################
pick_no = 8

# Track who has been drafted
my_drafted_player_indices = \
    [170, 80, 132, 165, 66, 82, 86, 21, 182, 46, 190, 67]

other_drafted_player_indices = \
    [131, 75, 14, 177, 188, 117, 9, 166, 136,
     133, 172, 196, 146, 83, 19, 8, 25, 161,
     96, 124, 93, 147, 26, 125, 54, 39, 38,
     30, 45, 12, 37, 79, 144, 195, 35, 1,
     148, 7, 3, 44, 73, 183, 154, 69, 168,
     163, 63, 48, 106, 100, 4, 111, 72, 60, 40,
     135, 103, 47, 27, 87, 158, 123, 186,
     70, 74, 11, 104, 185, 159, 22, 2,
     41, 10, 112, 98, 114, 28, 193, 56,
     184, 53, 55, 140, 130, 120, 153, 97,
     145, 23, 143, 78, 15, 138, 116, 169, 17,
     113, 122, 109, 6, 77, 59, 175, 134,
     176, 152, 127, 91, 62, 57,
     101, 34]


untracked_drafted = 9
print '%s players taken' % (untracked_drafted + len(my_drafted_player_indices) + len(other_drafted_player_indices))
"""
List them here: maclin; mcfadden; woodhead; gore
"""
########################################################

num_teams = 10
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
print 'TEAM:'
for player in my_drafted_players:
    print '\t %s' % player.id

