from .player import Player
#for each player create regressiontree etc to calculate xg, xa, xdc, xgc etc and then calculate total points by adding them (depending on position)
class Goalkeeper(Player):
    def __init__(self, player: dict, team_name: str):
        super().__init__(player, team_name)
        self.penalties_saved = player["penalties_saved"]
        self.goals_conceded = player["goals_conceded"]
        self.saves = player["saves"]
        self.calculate_pts_form()  #for eaach fixture caclulate points based off stats