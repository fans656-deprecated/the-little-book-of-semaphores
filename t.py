from threading import Semaphore, Thread
from Queue import Queue
import threading
import time

class FIFO(object):

    def __init__(self):
        self.queue = Queue()
        self.lock = Semaphore(1)

    def wait(self):
        s = Semaphore(0)
        self.lock.acquire()
        self.queue.put(s)
        self.lock.release()
        s.acquire()

    def signal(self):
        self.lock.acquire()
        s = self.queue.get()
        self.lock.release()
        s.release()

def f_gen(i):
    def f():
        fifo.wait()
        print i
    return f

fifo = FIFO()

fs = [f_gen(i) for i in range(5)]
ts = [Thread(target=f) for f in fs]
for t in ts:
    t.start()
for _ in range(5):
    time.sleep(0.1)
    fifo.signal()
