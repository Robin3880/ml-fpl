from .team import Team

class Player:
    def __init__(self, player: dict, team: Team, position: str):
        self.value = player.get("now_cost", 0) 
        self.id = player["id"]
        self.position = player["element_type"]
        self.first_name = player["first_name"]
        self.second_name = player["second_name"]
        self.web_name = player["web_name"]
        self.team = team
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

    
