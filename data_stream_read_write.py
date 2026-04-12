class SimpleInputStream:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def read(self, n=1):
        chunk = self.data[self.pos:self.pos+n]
        self.pos += len(chunk)
        return chunk
