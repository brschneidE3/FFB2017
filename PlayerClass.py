
class Player:

    def __init__(self, identifier):

        self.id = identifier
        self.position = self.get_position()

    def add_points(self, weekly_points):

        self.points = weekly_points
        self.total_points = sum(weekly_points.values())

    def add_avg_pick(self, avg_pick):

        self.avg_pick = avg_pick

    def get_position(self):

        parse_for_positions = self.id.rsplit(' - ')

        if len(parse_for_positions) != 2:
            print 'Error solving for position for %s' % self.id
            exit()
        else:
            position_string = parse_for_positions[1]
            positions = position_string.rsplit(',')
            if len(positions) > 1:
                print 'Multiple positions found for %s' % self.id
                exit()
            else:
                position = positions[0]
                if position in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']:
                    return position
                elif position in ['S', 'CB']:
                    return 'DB'
                elif position in ['LB', 'DE', 'DL']:
                    return 'D'
                else:
                    print 'Unidentified position for: %s' % self.id