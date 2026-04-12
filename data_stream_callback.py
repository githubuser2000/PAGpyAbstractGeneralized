class PushStream:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, fn):
        self.subscribers.append(fn)

    def push(self, value):
        for fn in self.subscribers:
            fn(value)
