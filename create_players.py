import csv
import PlayerClass
import pickle
import helpers

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
                try:
                    points = {i - 1: float(row[i]) for i in range(2, 18)}
                except ValueError:
                    points = {i - 1: 0 for i in range(2, 18)}

                player = PlayerClass.Player(player_id)
                player.add_points(points)
                players[player_id] = player

    return players

def save_players(players=None):

    players = create_players() if players is None else players

    # Save to pkl
    with open('players.pkl', 'wb') as playersfile:
        pickle.dump(players, playersfile, pickle.HIGHEST_PROTOCOL)

def load_players():
    with open('players.pkl', 'rb') as playersfile:
        players = pickle.load(playersfile)

        return players