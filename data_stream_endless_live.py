import time

def live_stream():
    i = 0
    while True:
        time.sleep(1)
        yield i
        i += 1
