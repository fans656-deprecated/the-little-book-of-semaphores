from threading import Semaphore

from tester import put, tester

class Barrier(object):

    def __init__(self, nThreads=2):
        self.__nThreads = nThreads
        self.__nArrived = 0
        self.__nArrived_lock = Semaphore(1)
        self.__allArrived = Semaphore(0)

    def wait(self):
        self.__nArrived_lock.acquire()
        self.__nArrived += 1
        self.__nArrived_lock.release()
        if self.__nArrived == self.__nThreads:
            self.__nArrived = 0
            for _ in range(self.__nThreads - 1):
                self.__allArrived.release()
        else:
            self.__allArrived.acquire()

r = Barrier(3)

def a():
    for _ in range(2):
        put('a1')
        r.wait()
        put('a2')
        r.wait()

def b():
    for _ in range(2):
        put('b1')
        r.wait()
        put('b2')
        r.wait()

def c():
    for _ in range(2):
        put('c1')
        r.wait()
        put('c2')
        r.wait()

tester.add(a, b, c)
tester.run()

