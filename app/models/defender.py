from .player import Player
from .team import Team
#for each player create regressiontree etc to calculate xg, xa, xdc, xgc etc and then calculate total points by adding them (depending on position)


class Defender(Player):
    def __init__(self, player: dict, team: Team, position: int, season: str = "current"):
        super().__init__(player, team, position, season)
        self.goals_scored = player["goals_scored"]
        self.expected_goals = player["expected_goals"]
        self.clean_sheets = player["clean_sheets"]
        self.expected_goals_conceded = player["expected_goals_conceded"]
        self.clearances_blocks_interceptions = player["clearances_blocks_interceptions"]
        self.recoveries = player["recoveries"]
        self.calculate_pts_form()  #for eaach fixture caclulate points based off stats



        