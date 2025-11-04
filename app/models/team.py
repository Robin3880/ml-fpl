from .teamfixture import TeamFixture


class Team():
    def __init__(self, data: dict):
        self.id = data["id"]
        self.name = data["name"]
        self.strength = data["strength"]
        self.fixtures = [None] * 5
        
    def __str__(self):
        return f"{self.id}, {self.name}, {self.fixtures}"
        