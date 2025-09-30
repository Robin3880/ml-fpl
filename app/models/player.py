class Player():
    def __init__(self, id, name, price, team): 
        self.name = name
        self.price = price
        self.team = team
        self._results = team.find_results()
        self._fixtures = team.find_fixtures()
        self.pts_form = self.calculate_pts_form()

    def calculate_pts_form(self):
        pass

    
