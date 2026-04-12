def infinite_stream():
    i = 0
    while True:
        yield i
        i += 1
