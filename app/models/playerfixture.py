from team import Team
class PlayerFixture():
    def __init__(self, goals=0, assists=0, yellow=0, red=0, bonus=0, bps=0, opponent: Team = None):
        self.goals = goals
        self.assists = assists
        self.yellow = yellow
        self.red = red
        self.bonus = bonus
        self.bps = bps
        self.opponent = opponent