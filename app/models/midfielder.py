from .player import Player
#for each player create regressiontree etc to calculate xg, xa, xdc, xgc etc and then calculate total points by adding them (depending on position)
class Midfielder(Player):
    def __init__(self, player: dict, team_name: str):
        super().__init__(player, team_name)
        self.goals_scored = player["goals_scored"]
        self.expected_goals = player["expected_goals"]
        self.clean_sheets = player["clean_sheets"]
        self.expected_goals_conceded = player["expected_goals_conceded"]
        self.calculate_pts_form()  #for eaach fixture caclulate points based off stats
