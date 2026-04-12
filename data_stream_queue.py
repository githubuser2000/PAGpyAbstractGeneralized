from queue import Queue
import threading

q = Queue()

def producer():
    for i in range(5):
        q.put(i)
    q.put(None)

def consumer():
    while True:
        item = q.get()
        if item is None:
            break
        print(item)

threading.Thread(target=producer).start()
threading.Thread(target=consumer).start()
