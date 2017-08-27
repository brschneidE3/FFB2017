
def pool_func(arg_tuple):

    player, prob_avail_after_dict, my_drafted_players, available_players, league = arg_tuple

    prob_avail_after = prob_avail_after_dict[player]

    if prob_avail_after < 1.0:
        team_with_player = my_drafted_players + [player]
        available_players.remove(player)

        # Create model instance
        model_w_player = league.create_optimal_model(team_with_player,
                                                     available_players,
                                                     prob_avail_after_dict)
        # Solve model instance
        solved_opt = league.solve_optimal_model(model_w_player)

        value = league.get_optimal_points(solved_opt)
        print player.id
        print '\t %s' % value

    else:
        value = 0

    return value


if __name__ == '__main__':

    from multiprocessing import Pool
    from draft_script import prob_avail_after_dict, available_players, my_drafted_players, league
    import time
    import operator
    import tabulate


    pool_start = time.time()
    pool = Pool(processes=8)

    args_iterable = \
        [(player, prob_avail_after_dict, my_drafted_players, available_players, league)
         for player in available_players]

    values = list(pool.imap(pool_func, args_iterable))
    pool.close()
    pool.join()
    pool_end = time.time()

    players_and_values = []
    for i in range(len(args_iterable)):
        player = args_iterable[i][0]
        value = values[i]
        players_and_values.append((player, value))

    sorted_players_and_values = sorted(players_and_values, key=operator.itemgetter(1), reverse=True)
    summary_table = []
    for i in range(len(sorted_players_and_values)):
        player, value = sorted_players_and_values[i]
        if value > 0:
            summary_table.append([player.id,
                                  int(value),
                                  int(sorted_players_and_values[i - 1][1] - value) if i > 0 else 0,
                                  int(sorted_players_and_values[0][1] - value)])
    print tabulate.tabulate(summary_table,['Player', 'Value', 'd_Value', 'cum_Value'])
    print '...Pool solving took %s seconds.\n' % round(pool_end - pool_start, 0)