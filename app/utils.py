import pandas as pd
import requests
from models.team import Team
from models.goalkeeper import Goalkeeper
from models.defender import Defender
from models.midfielder import Midfielder
from models.forward import Forward
from models.teamfixture import TeamFixture
from models.playerfixture import PlayerFixture

url = "https://fantasy.premierleague.com/api/bootstrap-static/"
data = requests.get(url).json()

 

current_gw = 0
for event in data["events"]:
    if event.get("is_current") is True:
        current_gw = event["id"]
        break

print(f"Current Gameweek is: {current_gw}")   #---------------------tests

teams = pd.DataFrame(data['teams'])
team_dict = {}
for _, team in teams.iterrows():
    id = team["id"]
    team_dict[id] = Team(team)
    
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

# get player data
for player_id, player_obj in player_dict.items():
    url = f"https://fantasy.premierleague.com/api/element-summary/{player_id}/"
    player_detail_data = requests.get(url).json()
    
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
        
        opponent_team_id = gw_data.get("opponent_team")                # change team so it shows its strength per results?-----------------------------------
        if opponent_team_id in team_dict:
                pf.opponent_strength = team_dict[opponent_team_id].strength




url = "https://fantasy.premierleague.com/api/fixtures/"
data = requests.get(url).json()

fixtures = pd.DataFrame(data)
for _, fixture in fixtures.iterrows():                    ##----use this api to get teams strenght per results?-------------------------------
    pass


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
