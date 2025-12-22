import os
import requests

seasons = [
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25"
]

# historical data path setup
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
data_dir = os.path.join(root_dir, "data", "historical")

if not os.path.exists(data_dir):
    os.makedirs(data_dir)


# fetch historical data and create csv for each season
for season in seasons:
    
    url = f"https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/{season}/gws/merged_gw.csv"

    season_data = os.path.join(data_dir, f"{season}.csv")
    response = requests.get(url)

    with open(season_data, "w", encoding="utf-8") as f:
        f.write(response.text)
            

        

