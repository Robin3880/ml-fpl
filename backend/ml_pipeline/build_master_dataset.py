import pandas as pd
import requests
import os
import io
import time
import json
import gc
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

def run_pipeline():
    # rate limiter for parallel api requests
    rate_lock = Lock()
    last_request_time = [0]

    SEASON = "2025-2026"
    REFRESH_CACHE = True 

    # MERGE CURRENT SEASON DATA FROM OFFICIAL FPL API AND OLBAUDAY FPL CORE INSIGHTS GITHUB INTO ONE MASTER CSV TO USE SO I HAVE MAXIMUM DATA

    # cache path setup 
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    data_folder = os.path.join(root_dir, "data")
    cache_folder = os.path.join(root_dir, "player_cache")

    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; ml_fpl/1.0; +https://github.com/Robin3880/ml-fpl)"})

    # get static fpl api data for players and current gw
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    fpl_static = session.get(url).json()

    current_gw = 0
    for event in fpl_static["events"]:    # current gameweek
        if event.get("is_current") is True:
            current_gw = event["id"]
            break

    players_dict = {}   
    for player in fpl_static["elements"]:
        players_dict[player["id"]] = {
            "name": player["web_name"],
            "team_id": player["team"],
            "position": player["element_type"],
        }

    # get fpl fixtures data for team strengths and context
    fixtures_url = "https://fantasy.premierleague.com/api/fixtures/"
    fixtures = session.get(fixtures_url).json()

    fixture_dict = {}
    for fixture in fixtures:
        fixture_dict[fixture["id"]] = {
            "h_team": fixture["team_h"],
            "a_team": fixture["team_a"],
            "h_diff": fixture["team_h_difficulty"],
            "a_diff": fixture["team_a_difficulty"],
            "gw": fixture["event"]
        }

    # get advanced data from github 
    github_url = f"https://raw.githubusercontent.com/olbauday/FPL-Core-Insights/main/data/{SEASON}"

    teams_df = pd.DataFrame(fpl_static["teams"])
    code_to_id_dict = dict(zip(teams_df["code"], teams_df["id"]))
    del teams_df
    gc.collect()

    stats_dict = {} # player stats
    match_data_dict = {} # scores and elo etc

    for gw in range(1, current_gw):
        # 1. Get Matches for this GW
        response = session.get(f"{github_url}/By Gameweek/GW{gw}/matches.csv")    
        matches_df = pd.read_csv(io.StringIO(response.text))
        
        # add fpl team id's
        matches_df["home_id"] = matches_df["home_team"].map(code_to_id_dict)
        matches_df["away_id"] = matches_df["away_team"].map(code_to_id_dict)
        
        # match scores and elo
        for m_row in matches_df.to_dict("records"):
            if m_row["tournament"] != "prem":
                continue
            m_id = m_row.get("match_id")
            match_data_dict[m_id] = {
                "home_id": m_row["home_id"],
                "away_id": m_row["away_id"],
                "home_score": m_row["home_score"],
                "away_score": m_row["away_score"],
                "home_team_elo": m_row["home_team_elo"],
                "away_team_elo": m_row["away_team_elo"],
                "home_xgc": m_row["away_expected_goals_xg"], 
                "away_xgc": m_row["home_expected_goals_xg"]
            }
        del matches_df  
        gc.collect()

        # player match stats
        response = session.get(f"{github_url}/By Gameweek/GW{gw}/playermatchstats.csv")
        stats_df = pd.read_csv(io.StringIO(response.text))
        
        # add match stats to dict with triple key
        for row in stats_df.to_dict("records"):
            if row["match_id"] not in match_data_dict:   # not a prem game
                continue

            team = int(players_dict[row["player_id"]]["team_id"])
            match_info = match_data_dict[row["match_id"]]

            h_id = int(match_info["home_id"])
            a_id = int(match_info["away_id"])
            if team == h_id:
                opponent_id = a_id
            else:
                opponent_id = h_id

            key = row["player_id"], gw, int(opponent_id)  # each player match stat can be accessed by triple key:   player id + gw ( + opponenet id    incase of double gameweek)
            stats_dict[key] = row
        
        del stats_df  
        gc.collect()
                
    # merge fpl and github data
    rows = []

    def fetch_player_data(player_id, cache_folder):
        cache_file = os.path.join(cache_folder, f"player_{player_id}.json")
        
        if not REFRESH_CACHE and os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                return player_id, json.load(f)
        else:
            with rate_lock:  # only one thread can access at time
                time_since_last = time.time() - last_request_time[0]
                if time_since_last < 0.01:  # limit to request every 0.01s
                    time.sleep(0.01 - time_since_last)  # wait remaining time
                last_request_time[0] = time.time()  

            response = session.get(f"https://fantasy.premierleague.com/api/element-summary/{player_id}/")
            history_data = response.json()
            with open(cache_file, "w") as f:
                json.dump(history_data, f)
            return player_id, history_data

    # fetch players in parrallel
    rows = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_player_data, pid, cache_folder): pid 
                for pid in players_dict.keys()}
        
        for future in futures:
            player_id, history_data = future.result()
            data = players_dict[player_id]
            
            for match in history_data["history"]:
                gameweek = match["round"]
                fixture_id = match["fixture"]
                opponent_id = match["opponent_team"]
                was_home = match["was_home"]
                
                row = {   # data needed from fpl api
                    "name": data["name"],
                    "player_id": player_id,
                    "team_id": data["team_id"],
                    "position": data["position"],
                    "gameweek": gameweek,
                    "kickoff_time": match["kickoff_time"],
                    "was_home": 1 if was_home else 0,
                    "opponent_id": opponent_id,
                    "value": match["value"],
                    "total_points": match["total_points"],
                    "minutes": match["minutes"],
                    "goals_scored": match["goals_scored"],
                    "assists": match["assists"],
                    "clean_sheets": match["clean_sheets"],
                    "goals_conceded": match["goals_conceded"], 
                    "own_goals": match["own_goals"],
                    "penalties_saved": match["penalties_saved"],
                    "penalties_missed": match["penalties_missed"],
                    "yellow_cards": match["yellow_cards"],
                    "red_cards": match["red_cards"],
                    "saves": match["saves"],
                    "bonus": match["bonus"],
                    "bps": match["bps"],
                    "influence": match["influence"],
                    "creativity": match["creativity"],
                    "threat": match["threat"],
                    "ict_index": match["ict_index"],
                }
                
                # get strengths
                f_info = fixture_dict[fixture_id]
                if was_home:
                    row["team_strength"] = f_info["a_diff"]
                    row["opponent_strength"] = f_info["h_diff"]
                else:
                    row["opponent_strength"] = f_info["a_diff"]
                    row["team_strength"] = f_info["h_diff"]

                # add advanced stats from github
                key = (player_id, gameweek, int(opponent_id))
                adv = stats_dict.get(key, {})
                row["expected_goals"] = adv.get("xg", 0.0)
                row["expected_assists"] = adv.get("xa", 0.0)
                row["clearances"] = adv.get("clearances", 0)
                row["blocks"] = adv.get("blocks", 0)
                row["interceptions"] = adv.get("interceptions", 0)
                row["tackles"] = adv.get("tackles", 0)
                row["recoveries"] = adv.get("recoveries", 0)
                row["tackles_won"] = adv.get("tackles_won", 0)
                row["duels_won"] = adv.get("duels_won", 0)
                row["aerial_duels_won"] = adv.get("aerial_duels_won", 0)
                row["team_goals_conceded"] = adv.get("team_goals_conceded")
                row["headed_clearances"] = adv.get("headed_clearances", 0)
                row["duels_lost"] = adv.get("duels_lost", 0)
                row["ground_duels_won"] = adv.get("ground_duels_won", 0)
                row["fouls_committed"] = adv.get("fouls_committed", 0) 
                row["sweeper_actions"] = adv.get("sweeper_actions", 0)
                row["cbit"] = row["clearances"] + row["blocks"] + row["interceptions"] + row["tackles"]
                row["cbirt"] = row["cbit"] + row["recoveries"]     

                # get team elos and expected goals conceded
                m_info = match_data_dict.get(adv.get("match_id"), {})
                
                if was_home:
                    row["team_elo"] = m_info.get("home_team_elo")
                    row["opponent_elo"] = m_info.get("away_team_elo")
                    row["expected_goals_conceded"] = m_info.get("home_xgc")
                else:
                    row["team_elo"] = m_info.get("away_team_elo")
                    row["opponent_elo"] = m_info.get("home_team_elo")
                    row["expected_goals_conceded"] = m_info.get("away_xgc")

                rows.append(row)

    df_master = pd.DataFrame(rows)

    # calculate rolling stats
    last_6_metrics = [
            "minutes", 
            "total_points", 
            "expected_goals", 
            "expected_assists", 
            "expected_goals_conceded",
            "goals_scored", 
            "assists", 
            "clean_sheets", 
            "goals_conceded",
            "own_goals", 
            "penalties_saved", 
            "penalties_missed",
            "yellow_cards", 
            "red_cards", 
            "saves", 
            "bonus", 
            "bps",
            "influence", 
            "threat", 
            "ict_index",
            "cbit",
            "cbirt",
            "clearances",
            "blocks",
            "interceptions",
            "tackles",
            "recoveries",           
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

    last_3_metrics = [   
        "minutes",         
        "total_points",     
        "expected_goals",  
        "expected_assists", 
        "saves",           
        "bps",
        "cbit",
        "cbirt",
        "clearances",
        "blocks",
        "interceptions",
        "tackles",
        "recoveries",
    ]

    # Calculate Rolling 6
    for metric in last_6_metrics:
        df_master[f"last_6_{metric}"] = df_master.groupby("player_id")[metric].transform(
            lambda x: x.rolling(window=6, min_periods=1).sum()
        )

    # Calculate Rolling 3
    for metric in last_3_metrics:
        df_master[f"last_3_{metric}"] = df_master.groupby("player_id")[metric].transform(
            lambda x: x.rolling(window=3, min_periods=1).sum()
        )


    df_master["kickoff_time"] = pd.to_datetime(df_master["kickoff_time"])
    df_master = df_master.sort_values(by=["player_id", "gameweek"])
    df_master.fillna(0, inplace=True)

    # save master data csv
    output_path = os.path.join(data_folder, f"master_{SEASON}_data.csv")
    df_master.to_csv(output_path, index=False)

    del df_master
    del rows
    del stats_dict
    del match_data_dict
    gc.collect()
