class Source:
    def __iter__(self):
        for i in range(5):
            yield i

class Sink:
    def send(self, value):
        print("Sink:", value)

source = Source()
sink = Sink()

for x in source:
    sink.send(x)
