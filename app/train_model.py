import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error , r2_score
from skopt import BayesSearchCV
from skopt.space import Real, Integer
import os   
import pickle

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "..", "data", "training_data.csv")
training_df = pd.read_csv(data_path)

# prepare data/features and split using scikitlearn
features = [
    "opponent_difficulty", 
    "team_strength", 
    "was_home", 
    "position_id",
    "last_6_minutes", 
    "last_6_total_points", 
    "last_6_expected_goals", 
    "last_6_expected_assists", 
    "last_6_expected_goals_conceded",
    "last_6_goals_scored", 
    "last_6_assists", 
    "last_6_clean_sheets", 
    "last_6_goals_conceded",
    "last_6_own_goals", 
    "last_6_penalties_saved", 
    "last_6_penalties_missed",
    "last_6_yellow_cards", 
    "last_6_red_cards", 
    "last_6_saves", 
    "last_6_bonus", 
    "last_6_bps", 
    "last_6_influence", 
    "last_6_creativity", 
    "last_6_threat", 
    "last_6_ict_index",
    "last_3_minutes", 
    "last_3_total_points", 
    "last_3_expected_goals", 
    "last_3_expected_assists", 
    "last_3_saves", 
    "last_3_bps"
]

target = "total_points"

training_df = training_df[training_df["minutes"] > 0].copy()                         

X = training_df[features]
y = training_df[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=8)

# use BayesSearchCV to find best hyper parameters for the model
search_space     = {
    "max_depth": Integer(3, 10),                     
    "learning_rate": Real(0.01, 1, "log-uniform"), 
    "subsample": Real(0.5, 1.0),                   
    "colsample_bytree": Real(0.5, 1.0),          
    "colsample_bylevel": Real(0.5, 1.0),           
    "colsample_bynode": Real(0.5, 1.0),              
    "reg_alpha": Real(1e-9, 100, "log-uniform"),     
    "reg_lambda": Real(1e-9, 100, "log-uniform"),  
    "n_estimators": Integer(50, 5000),              
    "min_child_weight": Integer(1, 10),             
}

xgb_reg = xgb.XGBRegressor(random_state=8, n_jobs=1) 

opt = BayesSearchCV(
    xgb_reg,
    search_space, cv=5,
    n_iter=50,
    scoring="neg_mean_squared_error",
    random_state=8,
    n_jobs=-1
) 

opt.fit(X_train, y_train)

# use the best params found along with early stopping rounds to get final model
final_model = xgb.XGBRegressor(
    **opt.best_params_,
    random_state=8,
    n_jobs=-1,
    early_stopping_rounds=50 
)

final_model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=False
)

preds = final_model.predict(X_test)
mae = mean_absolute_error(y_test, preds)
r2 = r2_score(y_test, preds)

print(f"mae: {mae}")
print(f"r2:  {r2}")

# save model
model_dir = os.path.join(script_dir, "..", "models")
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

model_path = os.path.join(model_dir, "fpl_xgboost.pkl")
with open(model_path, "wb") as f:
    pickle.dump(final_model, f)




