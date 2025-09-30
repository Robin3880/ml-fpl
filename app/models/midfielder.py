from player import Player
#for each player create regressiontree etc to calculate xg, xa, xdc, xgc etc and then calculate total points by adding them (depending on position)
class Midfielder(Player):
    def __init__(self, data: dict, team_name: str):
        super().__init__(data, team_name)
        self.goals_scored = data["goals_scored"]
        self.expected_goals = data["expected_goals"]
        self.clean_sheets = data["clean_sheets"]
        self.expected_goals_conceded = data["expected_goals_conceded"]
        self.calculate_pts()  #for eaach fixture caclulate points based off stats
