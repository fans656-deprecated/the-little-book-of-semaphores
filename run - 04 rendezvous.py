from runner import run

s = '''
a
    a1
    a_done.signal()
    b_done.wait()
    a2

b
    b1
    b_done.signal()
    a_done.wait()
    b2

a_done = Semaphore(0)
b_done = Semaphore(0)
'''

r = run(s)#.show(pause=True)
#print len(r)
assert all(r('a1 < b2'))
assert all(r('b1 < a2'))
assert any(r('a1 < b1'))
assert any(r('a1 > b1'))
assert any(r('a2 < b2'))
assert any(r('a2 > b2'))
