from threading import Semaphore, Thread
import threading
import time

nBoy = 0
nGirl = 0
token = Semaphore(1)
bQueue = Semaphore(0)
gQueue = Semaphore(0)
gFinish = Semaphore(0)

def a():
    global nGirl, nBoy
    token.acquire()
    if nGirl > 0:
        nGirl -= 1
        gQueue.release()
    else:
        nBoy += 1
        token.release()
        bQueue.acquire()
    print 'B'
    gFinish.acquire()
    token.release()

def b():
    global nGirl, nBoy
    token.acquire()
    if nBoy > 0:
        nBoy -= 1
        bQueue.release()
    else:
        nGirl += 1
        token.release()
        gQueue.acquire()
    print 'G'
    gFinish.release()

boys = [Thread(target=f) for f in [a] * 5]
girls = [Thread(target=f) for f in [b] * 5]
print '== 5 boys are waiting'
for boy in boys:
    boy.start()

time.sleep(0.01)
print '== 2 girls arriving'
for girl in girls[:2]:
    girl.start()

time.sleep(0.01)
print '== 3 more girls arriving'
for girl in girls[2:]:
    girl.start()
