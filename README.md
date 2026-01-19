[![FastAPI](https://img.shields.io/badge/API-FastAPI-005571?style=flat-square&logo=fastapi)](https://fpl-fastapi.azurewebsites.net/docs)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=flat-square&logo=react)](https://ml-fpl.vercel.app/)
[![ML](https://img.shields.io/badge/ML-XGBoost-orange?style=flat-square)](https://xgboost.readthedocs.io/)
[![Azure](https://img.shields.io/badge/Hosted_on-Microsoft_Azure-0089D6?style=flat-square&logo=microsoft-azure&logoColor=white)](https://fpl-fastapi.azurewebsites.net/docs)

#  ML-FPL: Machine Learning Fantasy Premier League Optimal Team

> **Live Website:**[ https://ml-fpl.vercel.app/](https://ml-fpl.vercel.app/)

**ML-FPL** is a full stack application built for the Fantasy Premier League (FPL) game using Machine Learning and Linear Programming to predict player performances for upcoming fixtures using models built on historical data and mathematically optimizes a fantasy premier league team based on multiple parameters, adhering to the games rules and restrictions.

---

## > Features

- **xPts Predicting:** Custom **XGBoost** models optimised with Scikit-Optimize Bayesian Search to predict points.
- **Defensive Returns:** Specific defensive **XGBoost model** combined with Poisson to calculate the likelihood of defensive contribution points which were newly added to the game in 2025/2026 season.
- **Linear Optimisation:** Uses **PuLP** to find the mathematical best team and bench, adhering to the FPL budget, team limit, and formation rules.
- **Custom Parameters:**
    - **GW Range:** Optimise for 1-5 next Gameweeks for short or long term insights.
    - **Team Strategy:** Choose between Best XI for maximum xPts or Differential for low owned players whose performances will rank you up the most in FPL.
- **React Website:** Frontend built with React and Tailwind for visualising the optimal team, see players ranked, and get individual player stats.
- **Automated Updates:** backend has a  background scheduler to check the FPL API at 1 AM each day and get the current Gameweek. If there is a change it triggers a rebuild of the master dataset and generates new predictions.

---

## > Project Tech Stack

### Data Science & Backend (Python)
- **Pandas and NumPy:** For data manipulation/cleanup and feature engineering.
- **XGBoost:** For Gradient boosting regression models (Predicting xPts/xDefcons).
- **Scikit-Optimize:** For Bayesian Search hyperparameter tuning to find the best settings for the XGBoost models.
- **Scipy Poisson:** Finds probability for players to reach defensive contribution point thresholds.
- **PuLP:** Python Linear Programming library for team optimization algorithm.
- **FastAPI:** For efficient RESTful API backend.

### Frontend
- **React:** JavaScript Component based framework.
- **Tailwind:** Styling for the Website.
- **Axios:** Promise-based HTTP client for API calls.

### Infrastructure
- **Microsoft Azure:** To host and deploy FastAPI backend.
- **Vercel:** To host React frontend.

---

## > Project Pipeline

### 1. Data Ingestion
* **FPL Data:** Pulls historical and current season data from the official FPL API.
* **Defensive Data:** Merged detailed defensive statistics from GitHub community datasets.
* **Multi-Source Ingestion:** Combines and links the Official FPL API with the GitHub defensive data to create a more detailed feature set.

### 2. ML Modeling 
* **Feature Engineering:** Rolling averages, fixture difficulties, and form indicators.
* **XGBoost Models:**
    * **Base Model:** Predicts general expected points without defensive contribution points from new rules.
    * **Defensive Model:** Predicts defensive contributions.
* **Poisson Distribution:** Used for defensive model to calculate the probability of a player breaking defensive point thresholds (eg: a defender reaching 10 defensive contributions which results in an extra 2 pts).

### 3. Predictions
* Gets current season data and upcoming fixtures for every player.
* Predicts expected points for every player for the next 5 Gameweeks.

### 4. Best Team Optimization
* **Best XI Algorithm:** Uses the **PuLP** library to solve a advanced variation of the Knapsack problem.
* **Algorithm Constraints:**
    * Maximum 3 players form each team.
    * Total team cost must be within €100m budget.
    * Team must use valid FPL formation (1 GK, 3-5 DEF, 3-5 MID, 1-3 FWD, 11 total players).
* **Strategies:**
    * *Best XI:* Pure expected points maximization.
    * *Differential:* Limits player ownership percentages to find players with highest potential to rank you up relative to other fpl managers.

---

## > FastAPI RESTful API Endpoints

* `GET /api/best_team`: Returns the highest expected points starting 11 and bench.
    * *Parameters:* `num_of_gw` (int), `differential` (bool)
* `GET /api/players`: Returns full list of players sorted by xPts or xPts/cost.
    * *Parameters:* `num_of_gw` (int), `sort_by` (str)
* `GET /api/player/{id}`: Returns specific detailed stats for a individual player.
* `GET /health`: Returns health status and total loaded player count.

> **Live Interactive API:** The API endpoints are testable live with the FastAPI UI https://fpl-fastapi.azurewebsites.net/docs.
---

## > Installation / Setup

### Project Prerequisites:
* Python 3.10 or newer
* Node.js and npm

### FastAPI Backend Setup
```bash
# change directory to backend
cd backend

# install required dependencies
pip install -r requirements.txt

# run local fastapi server (accessible on http://localhost:8000/docs/)
uvicorn main:app --reload
```
### React Frontend Setup

```bash
# change directory to backend from root
cd frontend

# install required dependencies
npm install

# run local react server (accessible on http://localhost:5173)
npm run dev

