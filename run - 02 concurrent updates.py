from runner import run

s = '''
a
    temp = count
    count = temp + 1

b
    temp = count
    count = temp + 1

count = 0
'''

r = run(s).show()
print set(r.val())
