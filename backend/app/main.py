from fastapi import FastAPI, HTTPException
from backend.app.algorithm import solve_best_team
from ml_pipeline.predict import generate_predictions
from contextlib import asynccontextmanager

PLAYERS = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    global PLAYERS
    PLAYERS = generate_predictions()
    yield
    PLAYERS.clear()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def home():
    return {"message": "FPL API is running."}

@app.get("/api/best-team")
def get_best_team(num_of_gw: int = 1):
    if not PLAYERS:
        raise HTTPException(status_code=503, detail="player data missing")
    
    if num_of_gw > 5:
        raise HTTPException(status_code=400, detail="max gameweeks is 5") 

    result = solve_best_team(PLAYERS, num_of_gw=num_of_gw)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    # filter starters and bench
    starters = [p for p in result if p["starter"] == True]
    bench = [p for p in result if p["starter"] == False]

    return {
        "starters": starters,
        "bench": bench,
        "total_cost": sum(p["cost"] for p in result),
        "total_xp": sum(p["xpts"] for p in result)
    }