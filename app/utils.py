import pandas as pd
import requests
import os
from classes.fixture import Fixture
from classes.player import Player
import pickle
import io
import pulp

SEASON = "2025-2026"

script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
data_folder = os.path.join(root_dir, "data")

# fetch current gw
url = "https://fantasy.premierleague.com/api/bootstrap-static/"
data = requests.get(url).json()

current_gw = 0
for event in data["events"]:
    if event.get("is_current") is True:
        current_gw = event["id"]
        break
print(current_gw)

# make a dict converting team id to elo for current gameweek,  and a dict for storing players by team later
current_team_elos = {}
url = f"https://raw.githubusercontent.com/olbauday/FPL-Core-Insights/refs/heads/main/data/2025-2026/By Gameweek/GW{current_gw}/teams.csv"
response = requests.get(url)
df = pd.read_csv(io.StringIO(response.text))
current_team_elos = dict(zip(df["id"], df["elo"]))
player_dict_by_team = {team_id: {} for team_id in df["id"]}

# for each player, create Player class instance  
url = "https://fantasy.premierleague.com/api/bootstrap-static/"
data = requests.get(url).json()
for player in data["elements"]:
    player_dict_by_team[player["team"]][player["id"]] = Player(player)

# get next 5 gamweek fixtures,  for each fixture add to all players from that team
url = "https://fantasy.premierleague.com/api/fixtures/"
data = requests.get(url).json()
for f in data:
    if f["event"] and f["event"] >= current_gw and f["event"] - current_gw < 5:
        i = f["event"] - current_gw
        h_id = f["team_h"]
        a_id = f["team_a"]
        home_fixture = Fixture(f["team_a_difficulty"], f["team_h_difficulty"], current_team_elos[h_id], current_team_elos[a_id], 1)
        away_fixture = Fixture(f["team_h_difficulty"], f["team_a_difficulty"], current_team_elos[a_id], current_team_elos[h_id], 0)

        for player in player_dict_by_team[h_id]:
            player_dict_by_team[h_id][player].fixtures[i].append(home_fixture)

        for player in player_dict_by_team[a_id]:
            player_dict_by_team[a_id][player].fixtures[i].append(away_fixture)

# load in master df,  for each player calculate rollint stats 
player_stats = os.path.join(data_folder, f"master_{SEASON}_data.csv")
df = pd.read_csv(player_stats)

grouped = df.groupby("player_id")

last_6_metrics = [
    "minutes", 
    "total_points", 
    "expected_goals", 
    "expected_assists", 
    "expected_goals_conceded",
    "goals_scored", 
    "assists", 
    "clean_sheets", 
    "goals_conceded",
    "own_goals", 
    "penalties_saved", 
    "penalties_missed",
    "yellow_cards", 
    "red_cards", 
    "saves", 
    "bonus", 
    "bps",
    "influence", 
    "threat", 
    "ict_index",
    "cbit",
    "cbirt",
    "clearances",
    "blocks",
    "interceptions",
    "tackles",
    "recoveries",           
    "tackles_won",       
    "headed_clearances", 
    "duels_won",          
    "duels_lost",        
    "ground_duels_won",  
    "aerial_duels_won",   
    "fouls_committed",   
    "sweeper_actions",    
    "goals_conceded",
    "team_goals_conceded"
]

last_3_metrics = [   
    "minutes",         
    "total_points",     
    "expected_goals",  
    "expected_assists", 
    "saves",           
    "bps",
    "cbit",
    "cbirt",
    "clearances",
    "blocks",
    "interceptions",
    "tackles",
    "recoveries",
]

# Calculate Rolling 6
for metric in last_6_metrics:
    df[f"last_6_{metric}"] = df.groupby("player_id")[metric].transform(
        lambda x: x.rolling(window=6, min_periods=1).sum()
    )

# Calculate Rolling 3
for metric in last_3_metrics:
    df[f"last_3_{metric}"] = df.groupby("player_id")[metric].transform(
        lambda x: x.rolling(window=3, min_periods=1).sum()
    )

# reduce dataframe to only current state of player
df = df.sort_values("gameweek").groupby("player_id").last().reset_index()

# get models I created
with open("models/fpl_xgboost.pkl", "rb") as f:
    base_model = pickle.load(f)

with open("models/fpl_defcon_xgboost.pkl", "rb") as f:
    defcon_model = pickle.load(f)

# for each player"s fixture predict points
player_list = []
for team_id in player_dict_by_team:
    for p_id in player_dict_by_team[team_id]:
        player = player_dict_by_team[team_id][p_id]
        player_list.append(player)
        stat_row = df[df["player_id"] == p_id]

        if not stat_row.empty:
            player.last_6 = {m: float(stat_row[f"last_6_{m}"].iloc[0]) for m in last_6_metrics}
            player.last_3 = {m: float(stat_row[f"last_3_{m}"].iloc[0]) for m in last_3_metrics}
        else:
            # new player with no stats
            player.last_6 = {m: 0.0 for m in last_6_metrics}
            player.last_3 = {m: 0.0 for m in last_3_metrics}

        player.predict_points(base_model, defcon_model)

# lp algorithm using pulp to build best expected points team
# constraints:
# 1.  100m budget  (82m for starting 11,  18m for 4 bench players)              
# 2.  valid formation  - 1gk,   min 3 def,  min 2 mid,   min 1 fwd                       
# 3.  max 3 players per club

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
    xpts[p.id] = p.gw_xp[0]
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
        selected.append((names[i], costs[i], xpts[i], "starter"))
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
bench_problem  += pulp.lpSum([defender[i] * sel_bench[i] for i in bench_ids]) == 5-num_def   # total 5 defenders
bench_problem  += pulp.lpSum([midfielder[i] * sel_bench[i] for i in bench_ids]) == 5-num_mid   # total 5 midfielders
bench_problem  += pulp.lpSum([forward[i] * sel_bench[i] for i in bench_ids]) == 3-num_fwd   # total 3 forwards

for team_id in team_map:
    allowed_slots = 3 - team_counts[team_id] # total 3 per team
    team_bench_players = [pid for pid in team_map[team_id] if pid in bench_ids] # number of selected bench players in that team
    bench_problem += pulp.lpSum([1 * sel_bench[i] for i in team_bench_players]) <= allowed_slots

bench_problem .solve(pulp.PULP_CBC_CMD(msg=False))
for i in bench_ids:
    if sel_bench[i].varValue == 1: # selected players
        selected.append((names[i], costs[i], xpts[i], "bench"))

# print best team 11,  and the 4 subs
for player in selected:
    print(f"{player[0]}, {player[1]}, {player[2]}, {player[3]}")