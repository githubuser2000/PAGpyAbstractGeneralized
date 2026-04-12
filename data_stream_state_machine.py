class StateStream:
    def __init__(self, state):
        self.state = state

    def step(self):
        value = self.state
        self.state += 1
        return value
