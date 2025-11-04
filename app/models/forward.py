from .player import Player
from .team import Team


#for each player create regressiontree etc to calculate xg, xa, xdc, xgc etc and then calculate total points by adding them (depending on position)
class Forward(Player):
    def __init__(self, player: dict, team: Team, season: str = "current"):
        super().__init__(player, team, season)
        self.goals_scored = player["goals_scored"]
        self.expected_goals = player["expected_goals"]
        self.calculate_pts_form()  #for each fixture caclulate points based off stats

    