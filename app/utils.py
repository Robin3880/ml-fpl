import pandas as pd
import requests
import os
import time
import json
from models.playerfixture import PlayerFixture
from models.team import Team
from models.goalkeeper import Goalkeeper
from models.defender import Defender
from models.midfielder import Midfielder
from models.forward import Forward

REFRESH_CACHE = False 

# player cache path setup 
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
cache_folder = os.path.join(root_dir, "player_cache")

if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)


# fetch current gw
url = "https://fantasy.premierleague.com/api/bootstrap-static/"
data = requests.get(url).json()

current_gw = 0
for event in data["events"]:
    if event.get("is_current") is True:
        current_gw = event["id"]
        break

print(f"Current Gameweek is: {current_gw}")  


# fetch teams
teams = pd.DataFrame(data['teams'])
team_dict = {}
for _, team in teams.iterrows():
    id = team["id"]
    team_dict[id] = Team(team)

# fetch players
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


# fetch team strengths per fixture
url = "https://fantasy.premierleague.com/api/fixtures/"
data = requests.get(url).json()

fixture_dict = {} 
fixtures = pd.DataFrame(data)

for _, fixture in fixtures.iterrows():
    fid = fixture["id"]
    fixture_dict[fid] = {
        "h_diff": fixture["team_h_difficulty"],
        "a_diff": fixture["team_a_difficulty"]
    }


# fetch player results data
for player_id, player_obj in player_dict.items():

    # file to store data for testing to minimize api requests
    cache_file = os.path.join(cache_folder, f"player_{player_id}.json")
    player_detail_data = None

    # check if player data exists in local cache,  if not then make api request and add it,     REFRESH_CACHE updates cache isntead
    if not REFRESH_CACHE and os.path.exists(cache_file):
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

            pf = PlayerFixture(position=player_obj.position)

            fid = gw_data["fixture"]
            was_home = gw_data["was_home"]
            if was_home:
                pf.opponent_strength = fixture_dict[fid]["h_diff"]
            else:
                pf.opponent_strength = fixture_dict[fid]["a_diff"]
            
            pf.gw = gw_data.get("round")
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


            player_obj.results.append(pf)


# --- PRINT PLAYERS ---
print("\n--- PLAYERS ---")
for i, player in enumerate(player_dict.values()):
    if i < 5: # limit to 5 players
        print(f"\nPlayer: {player.first_name} {player.second_name} ({player.team.name})")
        
        # filter games to see if played or not
        last_active_match = None
        games_played = [m for m in player.results if m.minutes > 0]
        
        if games_played:
            last_active_match = games_played[-1]
            print(f"---> Last Played (GW{last_active_match.gw}): Mins={last_active_match.minutes}, Goals={last_active_match.goals}, CS={last_active_match.clean_sheets}")
        else:
            print(f"---> No Games Played")
    
# --- PRINT ALL TEAMS ---
print("--- TEAMS ---")
for team in team_dict.values():
    print(team)
