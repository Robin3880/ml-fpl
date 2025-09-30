class Team():
    def __init__(self, id, name, league_position):
        self._id = id
        self.name = name
        self.league_position = league_position
        self._results = self.find_results()
        self._fixtures = self.find_fixtures()

    def find_results(self):
        pass
    
    def find_fixtures(self):
        pass