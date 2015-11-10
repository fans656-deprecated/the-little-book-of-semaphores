from runner import run

s = '''
a
    x = 5
    print = x

b
    x = 7

x = None
print = None
'''

r = run(s).show()
print set(r.val())
