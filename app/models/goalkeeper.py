from .player import Player
from .team import Team
#for each player create regressiontree etc to calculate xg, xa, xdc, xgc etc and then calculate total points by adding them (depending on position)


class Goalkeeper(Player):
    def __init__(self, player: dict, team: Team, position: int, season: str = "current"):
        super().__init__(player, team, position, season)
        self.penalties_saved = player["penalties_saved"]
        self.goals_conceded = player["goals_conceded"]
        self.saves = player["saves"]
        self.calculate_pts_form()  #for eaach fixture caclulate points based off stats
