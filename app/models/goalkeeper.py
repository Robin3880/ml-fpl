from player import Player
#for each player create regressiontree etc to calculate xg, xa, xdc, xgc etc and then calculate total points by adding them (depending on position)
class Goalkeeper(Player):
    def __init__(self, data: dict, team_name: str):
        super().__init__(data, team_name)
        self.penalties_saved = data["penalties_saved"]
        self.goals_conceded = data["goals_conceded"]
        self.saves = data["saves"]
        self.calculate_pts()  #for eaach fixture caclulate points based off stats