import pandas as pd
import os
import numpy as np

script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
data_dir = os.path.join(root_dir, "data", "historical_player_data")
fixtures_dir = os.path.join(root_dir, "data", "historical_fixture_data")


# add past seasons data to one dataframe
df = pd.DataFrame()

for filename in os.listdir(data_dir):
    # get season player data df and add season id
    file_path = os.path.join(data_dir, filename)
    season_df = pd.read_csv(file_path, on_bad_lines='skip')
    season_id = filename.replace(".csv", "")
    season_df["season_id"] = season_id

    # add fixture difficulty
    file_path = os.path.join(fixtures_dir, f"{season_id}_fixtures.csv")
    fixtures_df = pd.read_csv(file_path)
    fixtures_df = fixtures_df[["id", "team_h_difficulty", "team_a_difficulty"]]

    season_df = season_df.merge(fixtures_df, left_on='fixture', right_on='id', how='left')
    season_df['opponent_difficulty'] = np.where(season_df['was_home'] == True, season_df['team_h_difficulty'], season_df['team_a_difficulty'])
    season_df['team_strength'] = np.where(season_df['was_home'] == True, season_df['team_a_difficulty'], season_df['team_h_difficulty'])
    season_df.drop(columns=['id', 'team_h_difficulty', 'team_a_difficulty'], inplace=True)

    df = pd.concat([df, season_df])

# clean up
df['gameweek'] = df['GW'].fillna(df['round'])   # some seasons used round and some used GW so merge the two into one column
df.drop(columns=['GW', 'round'], inplace=True)
df['kickoff_time'] = pd.to_datetime(df['kickoff_time'])
df['player_season_id'] = df['name'] + "_" + df['season_id']  # create unique player-season id for each season
    

#  to add:
#  rolling results
#
#

