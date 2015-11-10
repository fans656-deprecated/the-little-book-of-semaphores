from runner import run

s = '''
a
    a1
    sem.signal()

b
    sem.wait()
    b1

sem = Semaphore(0)
'''

r = run(s).show()
assert all(r('a1 < b1'))
