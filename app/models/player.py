from team import Team
from playerfixture import PlayerFixture
#for each player create regressiontree etc to calculate xg, xa, xdc, xgc etc and then calculate total points by adding them (depending on position)
class Player:
    def __init__(self, data: dict, team: Team):
        self.id = data["id"]
        self.first_name = data["first_name"]
        self.second_name = data["second_name"]
        self.team = team
        self.selected_by_percent = data["selected_by_percent"]
        self.chance_of_playing_this_round = data["chance_of_playing_this_round"]
        self.element_type = data["element_type"]  # 1=GK, 2=DEF, 3=MID, 4=FWD
        self.points_per_game = data["points_per_game"]
        self.minutes = data["minutes"]
        self.own_goals = data["own_goals"]
        self.penalties_missed = data["penalties_missed"]
        self.yellow_cards = data["yellow_cards"]
        self.red_cards = data["red_cards"]
        self.bonus = data["bonus"]
        self.bps = data["bps"]
        self.assists = data["assists"]
        self.expected_assists = data["expected_assists"]
        self.expected_goal_involvements = data["expected_goal_involvements"]
        self.results = [None] * 5  #will be replaced by PlayerFixture objects

        self.fixtures = [None] * 5 #will be replaced by Team objects
        self.fixutres = find_fixtures()
        

    def calculate_pts_form(self):
        pass

    
