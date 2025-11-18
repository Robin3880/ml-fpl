import pandas as pd
import requests
import os
import time
import json
from models.team import Team
from models.goalkeeper import Goalkeeper
from models.defender import Defender
from models.midfielder import Midfielder
from models.forward import Forward

url = "https://fantasy.premierleague.com/api/bootstrap-static/"
data = requests.get(url).json()

current_gw = 0
for event in data["events"]:
    if event.get("is_current") is True:
        current_gw = event["id"]
        break

print(f"Current Gameweek is: {current_gw}")  

teams = pd.DataFrame(data['teams'])
team_dict = {}
for _, team in teams.iterrows():
    id = team["id"]
    team_dict[id] = Team(team)

# get players
players = pd.DataFrame(data['elements'])
player_dict = {}
for _, player in players.iterrows():
    team = team_dict[player["team"]]
    position = player["element_type"]
    id = player["id"]
    if position == 1:
        player_dict[id] = Goalkeeper(player, team, position, season="current")
    elif position == 2:
        player_dict[id] = Defender(player, team, position, season="current")
    elif position == 3:
        player_dict[id] = Midfielder(player, team, position, season="current")
    elif position == 4:
        player_dict[id] = Forward(player, team, position, season="current")

# get teams strength per result
url = "https://fantasy.premierleague.com/api/fixtures/"
data = requests.get(url).json()

fixtures = pd.DataFrame(data)
for _, fixture in fixtures.iterrows():                   
    gameweek = fixture["event"]

    if gameweek is None:
        continue

    team_h = fixture["team_h"]
    team_a = fixture["team_a"]
    team_dict[team_h].fixture_strengths[gameweek-1] = fixture["team_h_difficulty"]
    team_dict[team_a].fixture_strengths[gameweek-1] = fixture["team_a_difficulty"]


cache_folder = "player_cache"
if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)

# get player results data
for player_id, player_obj in player_dict.items():

    # file to store data for testing to minimize api requests
    cache_file = os.path.join(cache_folder, f"player_{player_id}.json")
    player_detail_data = None

    # check if player data exists in local cache,  if not then make api request and add it
    if os.path.exists(cache_file):
        
        with open(cache_file, "r") as f:
            player_detail_data = json.load(f)
    else:
        url = f"https://fantasy.premierleague.com/api/element-summary/{player_id}/"
        response = requests.get(url)
            
        player_detail_data = response.json()
        
        with open(cache_file, "w") as f:
            json.dump(player_detail_data, f)

        time.sleep(0.1) # delay request for api limits and to prevent 429 error
            
    if player_detail_data:
        for gw_data in player_detail_data["history"]:
            gameweek = gw_data["round"]

            pf = player_obj.results[gameweek - 1]
            pf.pts = gw_data.get("total_points")
            pf.minutes = gw_data.get("minutes")
            pf.goals = gw_data.get("goals_scored")
            pf.assists = gw_data.get("assists")
            pf.clean_sheets = gw_data.get("clean_sheets")
            pf.goals_conceded = gw_data.get("goals_conceded")
            pf.yellow = gw_data.get("yellow_cards")
            pf.red = gw_data.get("red_cards")
            pf.bonus = gw_data.get("bonus")
            pf.bps = gw_data.get("bps")
            pf.dc = gw_data.get("defensive_contribution")
            pf.pm = gw_data.get("penalties_missed")
            pf.ps = gw_data.get("penalties_saved")
            pf.xg = gw_data.get("expected_goals")
            pf.xa = gw_data.get("expected_assists")
            pf.xgc = gw_data.get("expected_goals_conceded")
            pf.opponent_strength = player_obj.team.fixture_strengths[gameweek-1]


# --- PRINT PLAYERS ---
print("\n==== PLAYERS ====")
for i, player in enumerate(player_dict.values()):
    if i < 5: # limit to first 5 players for 
        print(f"\nPlayer: {player.first_name} {player.second_name} ({player.team.name})")
        # show stats for the last gameweek they played in
        for gw in range(current_gw, 0, -1):
            if player.results[gw-1].minutes > 0:
                print(f"  -> Last Played GW{gw}: Mins={player.results[gw-1].minutes}, Goals={player.results[gw-1].goals}, CS={player.results[gw-1].clean_sheets}")
                break
    
# --- PRINT ALL TEAMS ---
# print("==== TEAMS ====")
# for team in team_dict.values():
#     print(team)
