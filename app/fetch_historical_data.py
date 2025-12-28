import os
import io
import requests
import pandas as pd

seasons = [ 
    "2022-23", # start with 22-23 as this is the first season expected assists and expected goals were tracked
    "2023-24",
    "2024-25"
]

# historical data path setup
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
data_dir = os.path.join(root_dir, "data", "historical_player_data")
fixtures_dir = os.path.join(root_dir, "data", "historical_fixture_data")

if not os.path.exists(data_dir):  
    os.makedirs(data_dir)
if not os.path.exists(fixtures_dir):
    os.makedirs(fixtures_dir)

# fetch historical data and create csv for each season
for season in seasons:
    # get player data
    url = f"https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/{season}/gws/merged_gw.csv"

    season_path = os.path.join(data_dir, f"{season}.csv")
    response = requests.get(url)

    with open(season_path, "w", encoding="utf-8") as f:
        f.write(response.text)

    # get fixture data so we can add fixture difficulties
    fixtures_url = f"https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/{season}/fixtures.csv"

    fixtures_path = os.path.join(fixtures_dir, f"{season}_fixtures.csv")
    fixtures_response = requests.get(fixtures_url)

    with open(fixtures_path, "w", encoding="utf-8") as f:
        f.write(fixtures_response.text)


# the vaastav github repo does not have defensive CBIT stats which are needed for the new 25/26 defcon points rules so will fetch this from a different github repo
# (defenders with with at least 10 CBIT get 2 extra points,  midfielders with at least 12 CBIRT get 2 extra points)            
# CBIT - clearances blocks interecpetions tackles
# CBIRT - clearances blocks interceptions recoveries tackles

# data only avaialable for 2024-2025 season onwards,    will use this to train a seperate defensive contribution pts predictor model
seasons = [
    "2024-2025"
]
defensive_dir = os.path.join(root_dir, "data", "historical_defensive_data")
if not os.path.exists(defensive_dir):
    os.makedirs(defensive_dir)

for season in seasons:
    # first get player df with team codes as we will need this to know if they are home or away later
    url = f"https://raw.githubusercontent.com/olbauday/FPL-Core-Insights/refs/heads/main/data/{season}/players/players.csv"
    response = requests.get(url)
    players_df = pd.read_csv(io.StringIO(response.text))  # io.StringIO allows pandas to immediatley read the text without saving to file first

    players_df = players_df[["player_id", "team_code"]]

    # get player match stats and add team code onto it
    url = f"https://raw.githubusercontent.com/olbauday/FPL-Core-Insights/refs/heads/main/data/{season}/playermatchstats/playermatchstats.csv"

    response = requests.get(url)

    stats_df = pd.read_csv(io.StringIO(response.text))
    stats_df = stats_df.merge(players_df, left_on="player_id", right_on="player_id", how="left")

    season_path = os.path.join(defensive_dir, f"{season}_defensive.csv")
    stats_df.to_csv(season_path, index=False)

    


