import os
import requests

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

# data only avaialable for 2024-2025 season,    will use this to train a seperate defensive contribution pts predictor model
defensive_dir = os.path.join(root_dir, "data")
if not os.path.exists(defensive_dir):
    os.makedirs(defensive_dir)

url = f"https://raw.githubusercontent.com/olbauday/FPL-Core-Insights/refs/heads/main/data/2024-2025/playermatchstats/playermatchstats.csv"

season_path = os.path.join(defensive_dir, f"2024-2025_defensive.csv")

response = requests.get(url)
with open(season_path, "w", encoding="utf-8") as f:
    f.write(response.text)


