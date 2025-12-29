import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error , r2_score
from skopt import BayesSearchCV
from sklearn.multioutput import MultiOutputRegressor
from skopt.space import Real, Integer
import os   
import pickle

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "..", "data", "defensive_training_data.csv")
training_df = pd.read_csv(data_path)
training_df = training_df[training_df["minutes_played"] > 0].copy()

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


# prepare data/features and split using scikitlearn
features = [
    "opponent_difficulty",
    "team_strength",
    "was_home",
    "position_id",
    "last_6_cbit", 
    "last_6_cbirt",
    "last_6_clearances", 
    "last_6_blocks", 
    "last_6_interceptions", 
    "last_6_tackles", 
    "last_6_recoveries",
    "last_6_minutes_played",
    "last_6_tackles_won", 
    "last_6_headed_clearances",
    "last_6_duels_won", 
    "last_6_duels_lost", 
    "last_6_ground_duels_won", 
    "last_6_aerial_duels_won", 
    "last_6_fouls_committed", 
    "last_6_sweeper_actions",
    "last_6_goals_conceded", 
    "last_6_team_goals_conceded",
    "last_3_cbit",
    "last_3_cbirt",
    "last_3_clearances",
    "last_3_blocks",
    "last_3_interceptions",
    "last_3_tackles",
    "last_3_recoveries",
    "last_3_minutes_played"
]


targets = ["cbit", "recoveries"]

X = training_df[features]
y = training_df[targets]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=8)

# use BayesSearchCV to find best hyper parameters for the model
search_space     = {
    "estimator__max_depth": Integer(3, 10),                     
    "estimator__learning_rate": Real(0.01, 0.3, "log-uniform"), 
    "estimator__subsample": Real(0.5, 1.0),                   
    "estimator__colsample_bytree": Real(0.5, 1.0),          
    "estimator__colsample_bylevel": Real(0.5, 1.0),           
    "estimator__colsample_bynode": Real(0.5, 1.0),              
    "estimator__reg_alpha": Real(1e-9, 100, "log-uniform"),     
    "estimator__reg_lambda": Real(1e-9, 100, "log-uniform"),  
    "estimator__n_estimators": Integer(100, 5000),              
    "estimator__min_child_weight": Integer(1, 10),             
}

# use count poisson as its better for what we are predicitng (counts of tackles, clearences etc)
xgb_reg = xgb.XGBRegressor(objective='count:poisson', random_state=8, n_jobs=1)    # handle multiple targets (cbit and recoveries)

multi_output_model = MultiOutputRegressor(xgb_reg)

opt = BayesSearchCV(
    multi_output_model,
    search_space, cv=5,
    n_iter=50,
    scoring="neg_mean_absolute_error",
    random_state=8,
    n_jobs=-1
) 

opt.fit(X_train, y_train)

# use the best params found along with early stopping rounds to get final model
best_params = {k.replace('estimator__', ''): v for k, v in opt.best_params_.items()}

final_model = xgb.XGBRegressor(
    **best_params,
    objective='count:poisson',
    random_state=8,
    n_jobs=-1,
)

final_model = MultiOutputRegressor(final_model)

final_model.fit(X_train, y_train,)

preds = final_model.predict(X_test)
mae = mean_absolute_error(y_test, preds)
r2 = r2_score(y_test, preds)

print(f"mae: {mae}")
print(f"r2:  {r2}")

# save model
model_dir = os.path.join(script_dir, "..", "models")
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

model_path = os.path.join(model_dir, "fpl_defcon_xgboost.pkl")
with open(model_path, "wb") as f:
    pickle.dump(final_model, f)





