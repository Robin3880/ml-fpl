from scipy.stats import poisson

class Player:
    def __init__(self, player: dict):
        self.value = player.get("now_cost", 0) 
        self.id = player["id"]
        self.team = player["team"]
        self.position = player["element_type"]
        self.first_name = player["first_name"]
        self.second_name = player["second_name"]
        self.web_name = player["web_name"]
        self.selected_by_percent = player.get("selected_by_percent", 0)   
        self.chance_of_playing_this_round = player["chance_of_playing_this_round"] 
        self.fixtures = [[],[],[],[],[]]
        self.gw_xp = [0] * 5
        self.last_6 = {}
        self.last_3 = {}

    def __str__(self):
        return f"{self.id}, {self.first_name}, {self.web_name}, {self.position}"
    
    def predict_points(self, base_model, defcon_model):
        for i, gw in enumerate(self.fixtures):
            for fixture in gw:
                # predict base points
                features = [
                    fixture.opponent_strength,
                    fixture.team_strength,
                    fixture.was_home,
                    self.position,
                    self.last_6["minutes"], 
                    self.last_6["total_points"], 
                    self.last_6["expected_goals"], 
                    self.last_6["expected_assists"], 
                    self.last_6["expected_goals_conceded"],
                    self.last_6["goals_scored"], 
                    self.last_6["assists"], 
                    self.last_6["clean_sheets"], 
                    self.last_6["goals_conceded"],
                    self.last_6["own_goals"], 
                    self.last_6["penalties_saved"], 
                    self.last_6["penalties_missed"],
                    self.last_6["yellow_cards"], 
                    self.last_6["red_cards"], 
                    self.last_6["saves"], 
                    self.last_6["bonus"], 
                    self.last_6["bps"], 
                    self.last_6["influence"], 
                    self.last_6["threat"], 
                    self.last_6["ict_index"],
                    self.last_3["minutes"], 
                    self.last_3["total_points"], 
                    self.last_3["expected_goals"], 
                    self.last_3["expected_assists"], 
                    self.last_3["saves"], 
                    self.last_3["bps"]
                ]
                xp = base_model.predict([features])[0]
                
                # predict defensive contributions
                features = [
                    fixture.opponent_elo,
                    fixture.team_elo,
                    int(fixture.was_home),
                    self.position, 
                    self.last_6["cbit"], 
                    self.last_6["cbirt"],
                    self.last_6["clearances"], 
                    self.last_6["blocks"], 
                    self.last_6["interceptions"], 
                    self.last_6["tackles"], 
                    self.last_6["recoveries"],
                    self.last_6["minutes"], 
                    self.last_6["tackles_won"], 
                    self.last_6["headed_clearances"],
                    self.last_6["duels_won"], 
                    self.last_6["duels_lost"], 
                    self.last_6["ground_duels_won"], 
                    self.last_6["aerial_duels_won"], 
                    self.last_6["fouls_committed"], 
                    self.last_6["sweeper_actions"],
                    self.last_6["goals_conceded"], 
                    self.last_6["team_goals_conceded"],
                    self.last_3["cbit"],
                    self.last_3["cbirt"],
                    self.last_3["clearances"],
                    self.last_3["blocks"],
                    self.last_3["interceptions"],
                    self.last_3["tackles"],
                    self.last_3["recoveries"],
                    self.last_3["minutes"] 
                ]
                results = defcon_model.predict([features])[0]
                xcbit = results[0]
                xrecoveries = results[1]

                self.calculate_total_points(xp, xcbit, xrecoveries, i)

    def get_start_probability(self):
        recent_avg_mins = self.last_3["minutes"] / 3
        
        if self.chance_of_playing_this_round == 0:
            return 0.05 # injured, most likely wont play at all
        
        if recent_avg_mins >= 80 or (self.last_6["minutes"]>20 and self.chance_of_playing_this_round == 100):
            return 1  # regular starter,  or regular starter who has returned from injury
        elif recent_avg_mins >= 20 and self.chance_of_playing_this_round == 75:
            return 0.8  # regular starter who has slight injury so might come off bench instead of starting
        elif self.last_6["minutes"] >= 45:  
            return 0.75   # non fixed starter
        elif recent_avg_mins > 20:
            return 0.60  # regular sub
        else:
            return 0.05

    def calculate_total_points(self, xp, xcbit, xrecoveries, gw):
        """
        helper method to calculate final xp taking into account everything
        
        :param self: this player
        :param xp: expected base points
        :param xcbit: expected cbit
        :param xrecoveries: expected recoveries
        :param gw: current gameweek
        """
        if self.position == 2:  # DEF
            prob_10_cbit = poisson.sf(9, xcbit)
            xp += prob_10_cbit*2
        elif self.position == 3 or self.position == 4: #MID or FWD
            prob_12_cbirt = poisson.sf(11, xcbit + xrecoveries)
            xp += prob_12_cbirt*2
        
        # add xp boosts to make it a less safe model and differentiate high point potential player 
        multipliers = {1:1.2, 2:1, 3:1, 4:2.2}  
        # boost high goal potential midfielders points more as these are worth more points thatn defcons/bp
        if self.position == 3 and self.last_6["expected_goals"] >= 2:
            boost = 1.1 + max(0, (self.last_6["expected_goals"] + self.last_6["expected_assists"]*(0.2) - 2.0) * 0.2)
            multipliers[3] = min(boost, 1.8)
        
        # boost high clean sheet potential defenders more as this is worth 4 points and more reliable/valuable than assists or defcons
        if self.position == 2:
            boost = 1 + ((8 - self.last_6["expected_goals_conceded"])*0.1) 
            multipliers[2] = max(min(boost, 1.5), 1) 

        if xp > 2.5:
            xp = 2.5 + ((xp - 2.5) * multipliers[self.position])

        self.gw_xp[gw] += xp * self.get_start_probability()



    
