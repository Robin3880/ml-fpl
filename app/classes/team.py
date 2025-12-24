class Team():
    def __init__(self, data: dict):
        self.id = data["id"]
        self.name = data["name"]
        self.strength = data["strength"] 
        self.strength_attack_home = data["strength_attack_home"]
        self.strength_attack_away = data["strength_attack_away"]
        self.strength_defence_home = data["strength_defence_home"]
        self.strength_defence_away = data["strength_defence_away"]
        
    def __str__(self):
        return f"{self.id}, {self.name}, {self.strength}"
        