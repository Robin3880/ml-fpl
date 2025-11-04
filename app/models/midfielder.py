from .player import Player
from .team import Team


class Midfielder(Player):
    def __init__(self, player: dict, team: Team, position: int, season: str = "current"):
        super().__init__(player, team, position, season)
        self.goals_scored = player["goals_scored"]
        self.expected_goals = player["expected_goals"]
        self.clean_sheets = player["clean_sheets"]
        self.expected_goals_conceded = player["expected_goals_conceded"]
        self.calculate_pts_form()  #for eaach fixture caclulate points based off stats
