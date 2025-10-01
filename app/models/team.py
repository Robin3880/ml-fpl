from .teamfixture import TeamFixture
class Team():
    def __init__(self, data: dict):
        self.id = data["id"]
        self.name = data["name"]
        self.short_name = data["short_name"]
        self.position = data["position"]
        self.results = [None] * 5  #will be replaced by TeamFixuture objects
        self.form = self.calculate_form()

    def __str__(self):
        return f"{self.id}, {self.short_name}, {[x.goals_scored for x in self.results]}"
        
    def calculate_form(self):
        pass