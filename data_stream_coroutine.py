def consumer():
    while True:
        item = yield
        print("Empfangen:", item)

c = consumer()
next(c)
c.send(10)
c.send(20)
