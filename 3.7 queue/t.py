from threading import Semaphore, Thread
import threading
import time

class Barrier(object):

    def __init__(self, nThread=2):
        self.nThread = nThread
        self.nArrive = 0
        self.nArrive_lock = Semaphore(1)
        self.allArrive = Semaphore(0)

    def wait(self):
        self.nArrive_lock.acquire()
        self.nArrive += 1
        self.nArrive_lock.release()
        if self.nArrive == self.nThread:
            self.nArrive = 0
            for _ in range(self.nThread - 1):
                self.allArrive.release()
        else:
            self.allArrive.acquire()

class Group(object):

    def __init__(self, nMember=2):
        self.nMember = nMember
        self.arrives = [Semaphore(0) for _ in range(nMember)]
        self.finishes = [Semaphore(0) for _ in range(nMember)]
        self.enters = [Semaphore(1) for _ in range(nMember)]

    def wait(self, iMember):
        self.arrives[iMember].release()
        for i in range(self.nMember):
            if i == iMember:
                continue
            self.arrives[i].acquire()
        self.enters[iMember].acquire()

    def leave(self, iMember):
        self.finishes[iMember].release()
        for i in range(self.nMember):
            if i == iMember:
                continue
            self.finishes[i].acquire()
        self.enters[iMember].release()

g = Group()

def a():
    g.wait(0)
    print 'B'
    g.leave(0)

def b():
    g.wait(1)
    print 'G'
    g.leave(1)

boys = [Thread(target=f) for f in [a] * 5]
girls = [Thread(target=f) for f in [b] * 5]
print '== 5 boys are waiting'
for boy in boys:
    boy.start()

time.sleep(1)
print '== 2 girls arriving'
for girl in girls[:2]:
    girl.start()

time.sleep(1)
print '== 3 more girls arriving'
for girl in girls[2:]:
    girl.start()
