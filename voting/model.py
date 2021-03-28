class RankedVote:

    def __init__(self, name, choices):
        self.name = name
        self.choices = choices
        self.ballots = []
        self.has_started = False
        self.has_ended = False
