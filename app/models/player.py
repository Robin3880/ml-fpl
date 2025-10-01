from .team import Team
from .playerfixture import PlayerFixture
#for each player create regressiontree etc to calculate xg, xa, xdc, xgc etc and then calculate total points by adding them (depending on position)
class Player:
    def __init__(self, player: dict, team: Team):
        self.id = player["id"]
        self.first_name = player["first_name"]
        self.second_name = player["second_name"]
        self.team = team
        self.selected_by_percent = player["selected_by_percent"]
        self.chance_of_playing_this_round = player["chance_of_playing_this_round"]
        self.element_type = player["element_type"]  # 1=GK, 2=DEF, 3=MID, 4=FWD
        self.points_per_game = player["points_per_game"]
        self.minutes = player["minutes"]
        self.own_goals = player["own_goals"]
        self.penalties_missed = player["penalties_missed"]
        self.yellow_cards = player["yellow_cards"]
        self.red_cards = player["red_cards"]
        self.bonus = player["bonus"]
        self.bps = player["bps"]
        self.assists = player["assists"]
        self.expected_assists = player["expected_assists"]
        self.expected_goal_involvements = player["expected_goal_involvements"]
        self.results = [None] * 5  #will be replaced by PlayerFixture objects

        self.fixtures = [None] * 5 #will be replaced by Team objects
        self.fixtures = self.find_fixtures()
    
    def __str__(self):
        return f"{self.id},{self.first_name},{self.team.name},{self.points_per_game}"

    def calculate_pts_form(self):
        pass
    def find_fixtures(self):
        pass

    
