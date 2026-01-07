import pandas as pd
import requests
import os
from classes.fixture import Fixture
from classes.player import Player
import pickle
import io

SEASON = "2025-2026"

# cache path setup 
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
    "creativity", 
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
        lambda x: x.rolling(window=6, min_periods=1).mean()
    )

# Calculate Rolling 3
for metric in last_3_metrics:
    df[f"last_3_{metric}"] = df.groupby("player_id")[metric].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean()
    )

# reduce dataframe to only current state of player
df = df.sort_values("gameweek").groupby("player_id").last().reset_index()

# get models I created
with open("models/fpl_xgboost.pkl", "rb") as f:
    base_model = pickle.load(f)

with open("models/fpl_defcon_xgboost.pkl", "rb") as f:
    defcon_model = pickle.load(f)

# for each player"s fixture predict points
for team_id in player_dict_by_team:
    for p_id in player_dict_by_team[team_id]:
        player = player_dict_by_team[team_id][p_id]
        stat_row = df[df["player_id"] == p_id]

        if not stat_row.empty:
            player.last_6 = {m: float(stat_row[f"last_6_{m}"].iloc[0]) for m in last_6_metrics}
            player.last_3 = {m: float(stat_row[f"last_3_{m}"].iloc[0]) for m in last_3_metrics}
        else:
            # new player with no stats
            player.last_6 = {m: 0.0 for m in last_6_metrics}
            player.last_3 = {m: 0.0 for m in last_3_metrics}

        player.predict_points(base_model, defcon_model)






