from threading import Semaphore, Thread
from Queue import Queue
import threading
import time
import random

q = Queue()

def put(o):
    global q
    q.put(o)

class Lightswitch(object):

    def __init__(self):
        self.__n = 0
        self.__lock = Semaphore(1)

    def lock(self, semaphore):
        self.__lock.acquire()
        self.__n += 1
        if self.__n == 1:
            semaphore.acquire()
        self.__lock.release()

    def unlock(self, semaphore):
        self.__lock.acquire()
        self.__n -= 1
        if self.__n == 0:
            semaphore.release()
        self.__lock.release()

empty = Semaphore(1)
light = Lightswitch()

def writer():
    empty.acquire()
    put('write')
    empty.release()

def reader():
    light.lock(empty)
    put('read')
    light.unlock(empty)

rs = [Thread(target=reader) for _ in range(5)]
ws = [Thread(target=writer) for _ in range(3)]
ts = rs + ws
random.shuffle(ts)
for t in ts:
    t.start()

while True:
    print q.get()
