class Stream:
    def __init__(self, iterable):
        self.iterable = iterable

    def map(self, fn):
        return Stream(fn(x) for x in self.iterable)

    def filter(self, pred):
        return Stream(x for x in self.iterable if pred(x))

    def __iter__(self):
        return iter(self.iterable)
