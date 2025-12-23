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


            



