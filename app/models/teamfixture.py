from __future__ import annotations 


class TeamFixture():
    def __init__(self, status: str, goals_scored: int, goals_conceded: int, opponent: "Team"):
        self.status = status
        self.goals_scored = goals_scored
        self.goals_conceded = goals_conceded
        self.opponent = opponent
        self.opponent_strength = opponent.strength
