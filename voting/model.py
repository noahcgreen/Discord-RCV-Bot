import json


class RankedVote:

    def __init__(self, name, choices):
        self.name = name
        self.choices = choices
        # NxN matrix where N is the number of choices
        # votes[m][n] says how many voters listed choice m as rank n
        self.votes = []
        # Voters participating in this vote
        self.voters = []
        self.has_started = False
