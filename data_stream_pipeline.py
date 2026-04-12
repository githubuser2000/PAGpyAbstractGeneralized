def source():
    for i in range(10):
        yield i

def squares(xs):
    for x in xs:
        yield x * x

def evens(xs):
    for x in xs:
        if x % 2 == 0:
            yield x

pipeline = evens(squares(source()))

for x in pipeline:
    print(x)
