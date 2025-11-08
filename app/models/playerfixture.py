from .team import Team

class PlayerFixture():
    def __init__(self, pts=0, position=None, minutes=0, goals=0, assists=0, cs=0, gc=0, yellow=0, red=0, bonus=0, bps=0, dc=0, pm=0, ps=0, xg=0, xa=0, xgc=0, opponent_strength=0):
        self.position = position
        self.pts = pts
        self.minutes = minutes
        self.goals = goals
        self.assists = assists
        self.cs = cs
        self.gc = gc
        self.yellow = yellow 
        self.red = red
        self.bonus = bonus
        self.bps = bps
        self.dc = dc
        self.pm = pm
        self.ps = ps
        self.xg = xg
        self.xa = xa
        self.xgc = xgc
        self.opponent_strength = opponent_strength
