from teamfixture import TeamFixture
class Team():
    def __init__(self, data: dict):
        self.id = data["id"]
        self.name = data["name"]
        self.short_name = data["short_name"]
        self.position = data["position"]
        self.results = [None] * 5  #will be replaced by TeamFixuture objects
        self.form = self.calculate_form()

    def calculate_form(self):
        pass