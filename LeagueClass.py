import constants
from coopr import pyomo
import tabulate
import operator

class League:

    def __init__(self, num_teams, num_rounds, players):

        self.num_teams = num_teams
        self.num_rounds = num_rounds
        self.players = players

    def solve_optimal_model(self, model, printon=False):
        opt = pyomo.SolverFactory('cbc')
        opt.solve(model)

        if printon:
            self.print_points_by_player(model)
        return model

    def get_optimal_points(self, solved_opt):
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
        print 'OBJ VAL: %s\n' % self.get_optimal_points(solved_opt)

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

    def create_optimal_model(self, team_playerids, available_playerids, prob_avail_after):

        model = pyomo.ConcreteModel()
        model.weeks = constants.week_weights.keys()
        model.positions = constants.roster.keys()
        model.roster_size = sum(constants.roster.values())

        model.team_players = [self.players[id] for id in team_playerids]
        model.avail_players = [self.players[id] for id in available_playerids]
        model.players = model.team_players + model.avail_players

        model.prob_avail_after = {key: prob_avail_after[key] for key in prob_avail_after.keys()}
        for player in model.team_players:
            if player in model.team_players:
                model.prob_avail_after[player] = 1.0

        # Decision variable for whether player is playing or not
        model.starting = pyomo.Var(model.players, model.positions, model.weeks, within=pyomo.Binary)
        # Decision variable for whether player is used or not
        model.starts = pyomo.Var(model.players, within=pyomo.NonNegativeIntegers)
        model.used = pyomo.Var(model.players, within=pyomo.Binary)

        # Objective function
        model.objective = pyomo.Objective(rule=self.objective, sense=pyomo.maximize)

        # Constraints
        model.position_eligibility = pyomo.Constraint(model.players, model.positions, model.weeks, rule=self.position_eligibility)
        model.weekly_roster_size = pyomo.Constraint(model.positions, model.weeks, rule=self.weekly_roster_size)
        model.only_one_position = pyomo.Constraint(model.players, model.weeks, rule=self.only_one_position)
        model.set_starts = pyomo.Constraint(model.players, rule=self.set_starts)
        model.set_used = pyomo.Constraint(model.players, rule=self.set_used)
        model.set_used2 = pyomo.Constraint(model.players, rule=self.set_used2)
        model.cap_used = pyomo.Constraint(model.players, rule=self.cap_used)

        return model

    @staticmethod
    def objective(model):
        # Maximize points scored by the roster
        obj_total = 0

        for player in model.players:
            player_total = 0
            for position in model.positions:
                if position != 'B':
                    for week in model.weeks:
                        week_weight = constants.week_weights[week]
                        player_total += player.points[week]*model.starting[player, position, week]*week_weight
            risk_scalar = model.prob_avail_after[player]
            player_exp_total = player_total * risk_scalar
            obj_total += player_exp_total

        return obj_total

    @staticmethod
    # Player can only play at positions they are eligible for, and the bench
    def position_eligibility(model, player, position, week):
        if player.position in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']:
            return model.starting[player, position, week] <= (player.position == position or position == 'B')
        elif player.position in ['D']:
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