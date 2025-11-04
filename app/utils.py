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

 
for event in data["events"]:  #assumes season has started
    if not event["is_next"]:
        current_gw = event["id"]
    else:
        break

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
        player_dict[id] = Goalkeeper(player, team, season="current")
    elif position == 2:
        player_dict[id] = Defender(player, team, season="current")
    elif position == 3:
        player_dict[id] = Midfielder(player, team, season="current")
    elif position == 4:
        player_dict[id] = Forward(player, team, season="current")

# get player minutes data
url = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/refs/heads/master/data/2025-26/player_idlist.csv"
df = pd.read_csv(url)
for _, player in df.iterrows():
    url = f"https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/refs/heads/master/data/2025-26/players/{player["first_name"]}_{player["second_name"]}_{player["id"]}/gws.csv"
    player_df = pd.read_csv(url)
    for i, gw in player_df.iterrows():
        player_dict[player["id"]].results[i].minutes = gw["minutes"]



url = "https://fantasy.premierleague.com/api/fixtures/"
data = requests.get(url).json()


fixtures = pd.DataFrame(data)
for _, fixture in fixtures.iterrows():
    gameweek = fixture["event"]
    if gameweek < current_gw:  #ignore current gw as maybe not all games are finished
        #assign player stats
        for stat in fixture["stats"]:
            identifier = stat["identifier"]  
            for side in ["a", "h"]:
                for entry in stat[side]:
                    player_id = entry["element"]
                    value = entry["value"]
                    player = player_dict[player_id]

                    pf = player.results[gameweek-1]
                    pf.opponent_strength = fixture["team_a_difficulty"] if side == "h" else fixture["team_h_difficulty"]

                    if identifier == "goals_scored":
                        pf.goals = value
                    elif identifier == "assists":
                        pf.assists = value
                    elif identifier == "yellow_cards":
                        pf.yellow = value
                    elif identifier == "red_cards":
                        pf.red = value
                    elif identifier == "bonus":
                        pf.bonus = value
                    elif identifier == "bps":
                        pf.bps = value
                    elif identifier == "defensive_contribution":
                        pf.dc = value
                    elif identifier == "penalties_missed":
                        pf.pm = value
                    elif identifier == "penalties_saved":
                        pf.ps = value
    elif 0 < (gameweek - current_gw) <= 5:  #get next 5 gw fixtures and add to future fixtures
        team_dict[fixture["team_a"]].fixtures[gameweek+1] = TeamFixture("away", fixture["team_a_score"], fixture["team_h_score"], team_dict[fixture["team_h"]])
        team_dict[fixture["team_h"]].fixtures[gameweek+1] = TeamFixture("home", fixture["team_h_score"], fixture["team_a_score"], team_dict[fixture["team_a"]])


# --- PRINT ALL PLAYERS ---
print("\n==== PLAYERS ====")
for player in player_dict.values():
    print(player)
    
# --- PRINT ALL TEAMS ---
print("==== TEAMS ====")
for team in team_dict.values():
    print(team)
