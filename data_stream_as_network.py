class Node:
    def __init__(self, fn):
        self.fn = fn
        self.targets = []

    def connect(self, other):
        self.targets.append(other)

    def send(self, value):
        result = self.fn(value)
        for t in self.targets:
            t.send(result)
