class Team():
    def __init__(self, data: dict):
        self.id = data["id"]
        self.name = data["name"]
        self.strength = data["strength"]
        self.fixtures = [None] * 5
        self.fixture_strengths = [None] * 38
        
    def __str__(self):
        return f"{self.id}, {self.name}, {self.fixtures}"
        