import pandas as pd
import os
import numpy as np
import io
import requests

script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
data_dir = os.path.join(root_dir, "data", "historical_player_data")
fixtures_dir = os.path.join(root_dir, "data", "historical_fixture_data")


# add past seasons data to one dataframe
df = pd.DataFrame()
all_seasons = [] 

for filename in os.listdir(data_dir):
    # get season player data df and add season id
    file_path = os.path.join(data_dir, filename)
    season_df = pd.read_csv(file_path, on_bad_lines="skip")
    season_id = filename.replace(".csv", "")
    season_df["season_id"] = season_id

    # add fixture difficulty
    file_path = os.path.join(fixtures_dir, f"{season_id}_fixtures.csv")
    fixtures_df = pd.read_csv(file_path)
    fixtures_df = fixtures_df[["id", "team_h_difficulty", "team_a_difficulty"]]

    season_df = season_df.merge(fixtures_df, left_on="fixture", right_on="id", how="left")
    season_df["opponent_difficulty"] = np.where(season_df["was_home"] == True, season_df["team_h_difficulty"], season_df["team_a_difficulty"])
    season_df["team_strength"] = np.where(season_df["was_home"] == True, season_df["team_a_difficulty"], season_df["team_h_difficulty"])
    season_df.drop(columns=["id", "team_h_difficulty", "team_a_difficulty"], inplace=True)

    all_seasons.append(season_df)

df = pd.concat(all_seasons, ignore_index=True)

# clean up
df["kickoff_time"] = pd.to_datetime(df["kickoff_time"])
df["player_season_id"] = df["name"] + "_" + df["season_id"]  # create unique player-season id for each season
pos_map = {"GK": 1, "GKP": 1, "DEF": 2, "MID": 3, "FWD": 4}
df["position_id"] = df["position"].map(pos_map)   # change position strings to int

# get rolling totals,   last 3  and last 6
df = df.sort_values(by=["player_season_id", "kickoff_time"])
grouped = df.groupby("player_season_id")

metrics = [
    "minutes", "total_points", 
    "expected_goals", "expected_assists", "expected_goals_conceded",
    "goals_scored", "assists", "clean_sheets", "goals_conceded",
    "own_goals", "penalties_saved", "penalties_missed",
    "yellow_cards", "red_cards", "saves", "bonus", "bps",
    "influence", "creativity", "threat", "ict_index"
]

key_metrics = [   # will be used to get recent form
    "minutes",         
    "total_points",     
    "expected_goals",  
    "expected_assists", 
    "saves",           
    "bps"
]

for metric in metrics:
    rolling_df = grouped[metric].rolling(window=6, min_periods=1, closed="left").sum()    # closed left removes the current row from calculation so you only get average of past 6

    df[f"last_6_{metric}"] = rolling_df.droplevel(0)   # remove multi index

for metric in key_metrics:
    rolling_df = grouped[metric].rolling(window=3, min_periods=1, closed="left").sum()    # closed left removes the current row from calculation so you only get average of past 6

    df[f"last_3_{metric}"] = rolling_df.droplevel(0)   # remove multi index

output_path = os.path.join(root_dir, "data", "training_data.csv")
df.to_csv(output_path, index=False)

# prepare defensive contributions data for seperate model
defensive_data = os.path.join(root_dir, "data", "historical_defensive_data")
df = pd.DataFrame()
all_seasons = []

for filename in os.listdir(defensive_data):
    # get season player data df and add season id
    file_path = os.path.join(defensive_data, filename)
    season_df = pd.read_csv(file_path, on_bad_lines="skip")
    season_id = filename.replace("_defensive.csv", "").replace(".csv", "")
    season_df["season_id"] = season_id

    # add fixture difficulty  (get fixtures from defensive stats inclusive github as different format to main data)
    url_fixtures = f"https://raw.githubusercontent.com/olbauday/FPL-Core-Insights/refs/heads/main/data/{season_id}/matches/matches.csv"
    response = requests.get(url_fixtures)
    fixtures_df = pd.read_csv(io.StringIO(response.text))
    fixtures_df = fixtures_df[["match_id", "home_team_elo", "away_team_elo", "home_team", "kickoff_time"]]

    season_df = season_df.merge(fixtures_df, left_on="match_id", right_on="match_id", how="left")

    season_df["was_home"] = np.where(season_df["home_team"] == season_df["team_code"], 1, 0)

    season_df["opponent_difficulty"] = np.where(season_df["was_home"] == True, season_df["away_team_elo"], season_df["home_team_elo"])
    season_df["team_strength"] = np.where(season_df["was_home"] == True, season_df["home_team_elo"], season_df["away_team_elo"])

    all_seasons.append(season_df)

df = pd.concat(all_seasons, ignore_index=True)

# clean up
df["kickoff_time"] = pd.to_datetime(df["kickoff_time"], format="mixed")
df["player_season_id"] = df["player_id"].astype(str) + "_" + df["season_id"]  # create unique player-season id for each season
pos_map = {"Goalkeeper": 1, "Defender": 2, "Midfielder": 3, "Forward": 4}
df["position_id"] = df["position"].map(pos_map)   # change position strings to int
df = df[(df["position_id"] == 2) | (df["position_id"] == 3)]
df = df.dropna(subset=["opponent_difficulty", "team_strength"])

# Defenders: C.B.I.T
df["cbit"] = (
    df["clearances"] + 
    df["blocks"] + 
    df["interceptions"] + 
    df["tackles"]
)

df["cbirt"] = df["cbit"] + df["recoveries"]


# get rolling totals,   last 3  and last 6
df = df.sort_values(by=["player_season_id", "kickoff_time"])
grouped = df.groupby("player_season_id")

metrics = [
    "cbit",
    "cbirt",
    "clearances",
    "blocks",
    "interceptions",
    "tackles",
    "recoveries",         
    "minutes_played",   
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

key_metrics = [   # will be used to get recent form
    "cbit",
    "cbirt",
    "clearances",
    "blocks",
    "interceptions",
    "tackles",
    "recoveries",
    "minutes_played"
]

for metric in metrics:
    rolling_df = grouped[metric].rolling(window=6, min_periods=1, closed="left").sum()    # closed left removes the current row from calculation so you only get average of past 6

    df[f"last_6_{metric}"] = rolling_df.droplevel(0)   # remove multi index

for metric in key_metrics:
    rolling_df = grouped[metric].rolling(window=3, min_periods=1, closed="left").sum()    # closed left removes the current row from calculation so you only get average of past 6

    df[f"last_3_{metric}"] = rolling_df.droplevel(0)   # remove multi index

output_path = os.path.join(root_dir, "data", "defensive_training_data.csv")
df.to_csv(output_path, index=False)
