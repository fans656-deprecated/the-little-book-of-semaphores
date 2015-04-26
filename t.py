from threading import Semaphore, Thread
from Queue import Queue
import threading
import time
import random

q = Queue()

def put(o):
    global q
    q.put(o)

writing = False
writing_lock = Semaphore(1)
operatings = 0
operatings_lock = Semaphore(1)
operating_finished = Semaphore(0)

def writer():
    operatings_lock.acquire()
    while operatings:
        operatings_lock.release()
        operating_finished.acquire()
        operatings_lock.acquire()
    writing_lock.acquire()
    writing = True
    writing_lock.release()
    put('WBeg')
    operatings_lock.release()
    put('write')
    put('WEnd')
    writing_lock.acquire()
    writing = False
    writing_lock.release()
    operating_finished.release()

def reader():
    global operatings
    operatings_lock.acquire()
    while writing:
        operatings_lock.release()
        operating_finished.acquire()
        operatings_lock.acquire()
    operatings += 1
    operatings_lock.release()
    put('{} beg'.format(threading.current_thread().ident))
    put('{} read'.format(threading.current_thread().ident))
    put('{} leave'.format(threading.current_thread().ident))
    operatings_lock.acquire()
    operatings -= 1
    operatings_lock.release()
    operating_finished.release()

ts = [Thread(target=reader) for _ in range(5)] + [Thread(target=writer) for _ in range(3)]
random.shuffle(ts)
for t in ts:
    t.start()

while True:
    print q.get()
