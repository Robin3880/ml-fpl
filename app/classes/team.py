class Team():
    def __init__(self, data: dict):
        self.id = data["id"]
        self.code = data["code"]
        self.name = data["name"]
        self.strength = data["strength"] 
        self.elo = data["elo"]
        self.code = data["code"]
        
    def __str__(self):
        return f"{self.id}, {self.name}, {self.strength}, {self.elo}"
        