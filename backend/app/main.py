from fastapi import FastAPI, HTTPException, Query
from backend.app.algorithm import solve_best_team
from ml_pipeline.predict import generate_predictions
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

PLAYERS = []
CURRENT_GW = 1

@asynccontextmanager
async def lifespan(app: FastAPI):
    global PLAYERS
    global CURRENT_GW
    PLAYERS, CURRENT_GW = generate_predictions()
    yield
    PLAYERS.clear()

app = FastAPI(lifespan=lifespan)

# use CORS so browser doesnt block requests (allow cross origin requests for react/fastapi)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # local host vite port for testing,  change to frontend url later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "FPL API is running."}

@app.get("/api/players/{player_id}")
def get_player_details(player_id: int):
    player = next((p for p in PLAYERS if p.id == player_id), None)
    
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    return {
        "id": player.id,
        "name": player.web_name,
        "cost": player.value,
        "position": player.position,
        "team": player.team,
        "selected_by_percent": player.selected_by_percent,
        "chance_of_playing_this_round": player.chance_of_playing_this_round,
        "xpts_predictions": {
            f"gw_{CURRENT_GW + 1}": float(player.gw_xp[0]),
            f"gw_{CURRENT_GW + 2}": float(player.gw_xp[1]),
            f"gw_{CURRENT_GW + 3}": float(player.gw_xp[2]),
            f"gw_{CURRENT_GW + 4}": float(player.gw_xp[2]),
            f"gw_{CURRENT_GW + 5}": float(player.gw_xp[2]),
        }
    }

@app.get("/api/best_team")
def get_best_team(num_of_gw: int = 1, differential: bool = False):
    if not PLAYERS:
        raise HTTPException(status_code=503, detail="player data missing")
    
    if num_of_gw > 5:
        raise HTTPException(status_code=400, detail="max gameweeks is 5") 

    result = solve_best_team(PLAYERS, num_of_gw, differential)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    # filter starters and bench
    starters = [p for p in result if p["starter"] == True]
    bench = [p for p in result if p["starter"] == False]

    return {
        "starters": starters,
        "bench": bench,
        "total_cost": sum(p["cost"] for p in result if p["starter"] == True),
        "total_xpts": sum(p["xpts"] for p in result if p["starter"] == True)
    }

@app.get("/api/players")
def get_players(num_of_gw: int = 1, sort_by: str = Query("xpts", enum=["xpts","xpts_per_cost"])):
    if not PLAYERS:
        raise HTTPException(status_code=503, detail="player data missing")
    
    if num_of_gw > 5:
        raise HTTPException(status_code=400, detail="max gameweeks is 5") 

    pos_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
    player_dicts = []

    for p in PLAYERS:
        player_dicts.append({
            "id": p.id,
            "name": p.web_name,
            "position": pos_map[p.position],
            "cost": int(p.value),
            "xpts": float(sum(p.gw_xp[0:num_of_gw])),    
            "xpts_per_cost": float(sum(p.gw_xp[0:num_of_gw]) / (p.value / 10))    
        })

    # sort by xpts or xpts per cost descending
    if sort_by == "xpts":
        player_dicts.sort(key=lambda x: x["xpts"], reverse=True)
    else:
        player_dicts.sort(key=lambda x: x["xpts_per_cost"], reverse=True)

    return player_dicts

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "players_loaded": len(PLAYERS),
    }