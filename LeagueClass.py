import constants
from coopr import pyomo
import tabulate
import operator
import PlayerClass

class League:

    def __init__(self, players):

        self.players = players

    def view_player_projections(self, player=None, player_i=None):
        player = player if player is not None else self.players.values()[player_i]
        player.view_projections()

    def print_num_pos(self):
        positions = {position: 0 for position in constants.ordered_positions if position != 'B'}

        for player in self.players.values():
            if 'Untracked' not in player.id:
                positions[player.position] += 1

        for position in constants.ordered_positions:
            if position != 'B':
                print '%s : %s' % (position, positions[position])

    def evaluate_trade(self, current_players, give_players, get_players):

        new_players = [player for player in current_players if player not in give_players] + get_players

        current_team_model = \
            self.create_optimal_model(current_players, [], {player: 1 for player in self.players.values()})
        solved_current_team = self.solve_optimal_model(current_team_model, printon=True)
        current_team_value = self.get_optimal_points(solved_current_team)

        print '\n'

        new_team_model = \
            self.create_optimal_model(new_players, [], {player: 1 for player in self.players.values()})
        solved_new_team = self.solve_optimal_model(new_team_model, printon=True)
        new_team_value = self.get_optimal_points(solved_new_team)

        trade_value = new_team_value - current_team_value

        print 'Current team projection: %s' % current_team_value
        print 'New team projection:     %s' % new_team_value
        print 'Value of trade:          %s' % trade_value

        return trade_value


    def solve_optimal_model(self, model, printon=False):
        opt = pyomo.SolverFactory('cbc')
        opt.solve(model)

        if printon:
            self.print_points_by_player(model)
        return model

    def print_starting(self, solved_opt):
        for week in pyomo.value(solved_opt.weeks):
            0

    def get_optimal_points(self, solved_opt=None):
        return pyomo.value(solved_opt.objective)

    def get_points_by_player(self, solved_opt):
        points_by_player = {}

        for player in solved_opt.players:
            for week in solved_opt.weeks:
                for position in solved_opt.positions:
                    if position != 'B' and solved_opt.starting[player, position, week]:
                        try:
                            points_by_player[player.id] += player.points[week]
                        except KeyError:
                            points_by_player[player.id] = player.points[week]

        return points_by_player

    def print_points_by_player(self, solved_opt):
        points_by_player = self.get_points_by_player(solved_opt)
        sorted_points_by_player = sorted(points_by_player.items(), key=operator.itemgetter(1), reverse=True)
        for player, points in sorted_points_by_player:
            print '%s: \n \t %s' % (player, points)
        print 'TOTAL: %s' % sum(points_by_player.values())

    def get_position_weeks_by_player(self, solved_opt):
        pos_wks_by_player = {}
        for position in constants.ordered_positions:
            for player in solved_opt.players:
                for week in solved_opt.weeks:
                    starting_at_pos = pyomo.value(solved_opt.starting[player, position, week])
                    try:
                        pos_wks_by_player[player, position] += starting_at_pos
                    except KeyError:
                        pos_wks_by_player[player, position] = starting_at_pos
        return pos_wks_by_player

    def print_position_weeks_by_player(self, solved_opt):
        pos_wks_by_player = self.get_position_weeks_by_player(solved_opt)
        data_table = []

        for player in solved_opt.players:
            new_row = [player.id]
            for position in constants.ordered_positions:
                new_row.append(pos_wks_by_player[player, position])
            if sum(new_row[1:]) > 0:
                data_table.append(new_row)

        headers = ['Player'] + constants.ordered_positions
        print tabulate.tabulate(data_table, headers=headers), '\n'

    def print_position_weeks_by_undrafted_player(self, solved_opt):
        pos_wks_by_player = self.get_position_weeks_by_player(solved_opt)
        data_table = []

        for player in solved_opt.players:
            if player in solved_opt.avail_players:
                new_row = [player.id]
                for position in constants.ordered_positions:
                    new_row.append(pos_wks_by_player[player, position])
                if sum(new_row[1:]) > 0:
                    data_table.append(new_row)

        headers = ['Player'] + constants.ordered_positions
        print tabulate.tabulate(data_table, headers=headers), '\n'

    def create_optimal_model(self, team_players, available_players, prob_avail_after):

        model = pyomo.ConcreteModel()

        # Set bounds of problem
        model.weeks = constants.week_weights.keys()
        model.positions = constants.roster.keys()
        model.roster_size = sum(constants.roster.values())

        mcfadden = PlayerClass.Player('D. McFadden Dal - RB')
        points = {1: 4.74, 2: 11.89, 3: 12.09, 4: 11.99, 5: 12.2, 6: 0, 7: 11.61, 8: 13.25, 9: 3.43, 10: 3.21, 11: 3.44, 12: 3.52,
                  13: 3.44, 14: 3.27, 15: 3.24, 16: 3.33}
        mcfadden.add_points(points)


        # Determine current and available players
        model.team_players = team_players + [mcfadden]
        model.avail_players = available_players
        model.players = model.team_players + model.avail_players

        model.prob_avail_after = {key: prob_avail_after[key] for key in prob_avail_after.keys()}
        for player in model.team_players:
            model.prob_avail_after[player] = 1.0

        ########### Decision Variables ###########
        model.starting = pyomo.Var(model.players, model.positions, model.weeks, within=pyomo.Binary)
        model.starts = pyomo.Var(model.players, within=pyomo.NonNegativeIntegers)
        model.used = pyomo.Var(model.players, within=pyomo.Binary)

        ########### Constraints ###########
        model.position_eligibility = pyomo.Constraint(model.players, model.positions, model.weeks, rule=self.position_eligibility)
        model.weekly_roster_size = pyomo.Constraint(model.positions, model.weeks, rule=self.weekly_roster_size)
        model.only_one_position = pyomo.Constraint(model.players, model.weeks, rule=self.only_one_position)
        model.set_starts = pyomo.Constraint(model.players, rule=self.set_starts)
        model.set_used = pyomo.Constraint(model.players, rule=self.set_used)
        model.set_used2 = pyomo.Constraint(model.players, rule=self.set_used2)
        model.cap_used = pyomo.Constraint(model.players, rule=self.cap_used)

        ########### Objective function ###########
        model.objective = pyomo.Objective(rule=self.objective, sense=pyomo.maximize)

        return model

    @staticmethod
    def objective(model):
        # Maximize points scored by the roster
        obj_total = 0

        for player in model.players:
            player_total = 0
            for position in model.positions:
                for week in model.weeks:
                    player_total += player.points[week]*model.starting[player, position, week]*(position != 'B')*constants.week_weights[week]
            risk_scalar = model.prob_avail_after[player]
            player_exp_total = player_total * risk_scalar
            obj_total += player_exp_total

        return obj_total

    @staticmethod
    # Player can only play at positions they are eligible for, and the bench
    def position_eligibility(model, player, position, week):
        if player.position in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']:
            return model.starting[player, position, week] <= (player.position == position or position == 'B')
        elif player.position == 'D':
            return model.starting[player, position, week] <= (position == 'D' or position == 'B')
        else:
            return model.starting[player, position, week] <= (position in ['D', 'DB', 'B'])

    @staticmethod
    # Limit the number of players playing a position
    def weekly_roster_size(model, position, week):
        return sum(model.starting[player, position, week] for player in model.players) <= constants.roster[position]

    @staticmethod
    # Only allow players to play 1 position each week
    def only_one_position(model, player, week):
        return sum(model.starting[player, position, week] for position in constants.ordered_positions) <= 1

    @staticmethod
    # Starts = the number of weeks not on the bench
    def set_starts(model, player):
        return model.starts[player] == \
               sum(model.starting[player, position, week] for position in model.positions if position != 'B' for week in model.weeks)

    @staticmethod
    # Squeeze used to 0 if player never starts
    def set_used(model, player):
        return model.used[player] <= model.starts[player]

    @staticmethod
    # Squeeze used to 1 if player starts
    def set_used2(model, player):
        return model.starts[player] <= model.used[player]*10000

    @staticmethod
    # Only allow roster_size many players to be used
    def cap_used(model):
        return sum(model.used[player] for player in model.players) <= model.roster_size