import pulp
from ml_pipeline.predict import generate_predictions
# lp algorithm using pulp to build best expected points team
# constraints:
# 1.  100m budget  (82m for starting 11,  18m for 4 bench players)              
# 2.  valid formation  - 1gk,   min 3 def,  min 2 mid,   min 1 fwd                       
# 3.  max 3 players per club

def solve_best_team(player_list, num_of_gw):
    my_lp_problem = pulp.LpProblem("FPL_LP_Problem", pulp.LpMaximize)

    ids = []
    costs = {}
    xpts = {}
    gk = {}
    defender = {}
    midfielder = {}
    forward = {}
    team_map = {}
    names = {}

    for p in player_list:
        ids.append(p.id)
        costs[p.id] = p.value
        xpts[p.id] = sum(p.gw_xp[0:num_of_gw])
        gk[p.id] = int(p.position == 1)
        defender[p.id] = int(p.position == 2)
        midfielder[p.id] = int(p.position == 3)
        forward[p.id] = int(p.position == 4)
        names[p.id] = p.web_name
        tid = p.team  
        if tid not in team_map:
            team_map[tid] = []
        team_map[tid].append(p.id)

    selections = pulp.LpVariable.dicts("selected", ids, cat='Binary')
    # objective  (max xp)
    my_lp_problem += pulp.lpSum([xpts[i] * selections[i] for i in ids])  
    # contraints
    my_lp_problem += pulp.lpSum([costs[i] * selections[i] for i in ids]) <= 820   # max 82m cost
    my_lp_problem += pulp.lpSum([1 * selections[i] for i in ids]) == 11   # 11 players
    my_lp_problem += pulp.lpSum([gk[i] * selections[i] for i in ids]) == 1   #  1 gk
    my_lp_problem += pulp.lpSum([defender[i] * selections[i] for i in ids]) >= 3   # min 3 defenders
    my_lp_problem += pulp.lpSum([defender[i] * selections[i] for i in ids]) <= 5   # max 5 defenders
    my_lp_problem += pulp.lpSum([midfielder[i] * selections[i] for i in ids]) >= 2   # min 2 midfielders
    my_lp_problem += pulp.lpSum([midfielder[i] * selections[i] for i in ids]) <= 5   # max 5 midfielders
    my_lp_problem += pulp.lpSum([forward[i] * selections[i] for i in ids]) >= 1   # min 1 forward
    my_lp_problem += pulp.lpSum([forward[i] * selections[i] for i in ids]) <= 3   # max 3 forward
    for team_id in team_map:
        players_in_team = team_map[team_id] # number of selected players in that team
        my_lp_problem += pulp.lpSum([selections[i] for i in players_in_team]) <= 3   # max 3 players per team

    my_lp_problem.solve(pulp.PULP_CBC_CMD(msg=False))

    # create best bench (remaining players)
    bench_ids = []
    num_def = 0
    num_mid = 0
    num_fwd = 0
    total_cost = 0
    selected = []
    team_counts = {tid: 0 for tid in team_map}

    for i in ids:
        if selections[i].varValue == 1: # selected players
            selected.append({"name":names[i], "cost":int(costs[i]), "xpts":float(xpts[i]), "starter":True})
            num_def += defender[i]
            num_mid += midfielder[i]
            num_fwd += forward[i]
            total_cost += costs[i]
            p_team = [t for t in team_map if i in team_map[t]][0] 
            team_counts[p_team] += 1
        else:
            bench_ids.append(i)

    bench_problem = pulp.LpProblem("FPL_LP_Problem", pulp.LpMaximize)
    sel_bench = pulp.LpVariable.dicts("bench", bench_ids, cat='Binary')
    # objective
    bench_problem  += pulp.lpSum([xpts[i] * sel_bench[i] for i in bench_ids])  
    # contraints
    bench_problem  += pulp.lpSum([costs[i] * sel_bench[i] for i in bench_ids]) <= 1000 - total_cost   # max 100m minus best 11 cost
    bench_problem  += pulp.lpSum([1 * sel_bench[i] for i in bench_ids]) == 4   # 4 players
    bench_problem  += pulp.lpSum([gk[i] * sel_bench[i] for i in bench_ids]) == 1   #  1 gk
    bench_problem += pulp.lpSum([costs[i] * sel_bench[i] for i in bench_ids if gk[i] == 1]) <= 45   #  bench gk not worth over 4.5m as will almost never be used compared to rest of bench
    bench_problem  += pulp.lpSum([defender[i] * sel_bench[i] for i in bench_ids]) == 5-num_def   # total 5 defenders
    bench_problem  += pulp.lpSum([midfielder[i] * sel_bench[i] for i in bench_ids]) == 5-num_mid   # total 5 midfielders
    bench_problem  += pulp.lpSum([forward[i] * sel_bench[i] for i in bench_ids]) == 3-num_fwd   # total 3 forwards

    for team_id in team_map:
        allowed_slots = 3 - team_counts[team_id] # total 3 per team
        team_bench_players = [pid for pid in team_map[team_id] if pid in bench_ids] # number of selected bench players in that team
        bench_problem += pulp.lpSum([1 * sel_bench[i] for i in team_bench_players]) <= allowed_slots

    bench_problem.solve(pulp.PULP_CBC_CMD(msg=False))
    for i in bench_ids:
        if sel_bench[i].varValue == 1: # selected players
            selected.append({"name":names[i], "cost":int(costs[i]), "xpts":float(xpts[i]), "starter":False})
    return selected
