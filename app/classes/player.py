from .team import Team

class Player:
    def __init__(self, player: dict, team: Team, position: str):
        self.value = player.get("now_cost", 0) 
        self.id = player["id"]
        self.position = position
        self.first_name = player["first_name"]
        self.second_name = player["second_name"]
        self.web_name = player["web_name"]
        self.team = team
        self.element_type = player.get("element_type")  # 1=GK,2=DEF,3=MID,4=FWD
        self.minutes = player.get("minutes", 0)
        self.points_per_game = player.get("points_per_game", 0)
        self.bonus = player.get("bonus", 0)
        self.bps = player.get("bps", 0)
        self.goals_scored = player.get("goals_scored", 0)
        self.expected_goals = player.get("expected_goals", 0)
        self.clean_sheets = player.get("clean_sheets", 0)
        self.expected_goals_conceded = player.get("expected_goals_conceded", 0)
        self.clearances_blocks_interceptions = player.get("clearances_blocks_interceptions", 0)
        self.recoveries = player.get("recoveries", 0)
        self.saves = player.get("saves", 0)
        self.assists = player.get("assists", 0)
        self.expected_assists = player.get("expected_assists", 0)
        self.penalties_missed = player.get("penalties_missed", 0)
        self.yellow_cards = player.get("yellow_cards", 0)
        self.red_cards = player.get("red_cards", 0)
        self.own_goals = player.get("own_goals", 0)
        self.selected_by_percent = player.get("selected_by_percent", 0)
        self.chance_of_playing_this_round = player["chance_of_playing_this_round"] 
        self.results = []
        self.fixtures = self.find_fixtures() 

    
    def __str__(self):
        return f"{self.id},{self.first_name},{self.team.name},{self.results}"

    def calculate_rolling(self):
        pass

    def find_fixtures(self):
        pass

    
