def paths(tree):

    def walk(root, children):
        q.append(root)
        if children:
            for c in children:
                walk(*c)
        else:
            ret.append(list(q))
        q.pop()

    q, ret = [], []
    walk(*tree)
    return ret

def gen(*ns):
    return [(i, gen(*(ns[:i] + (ns[i] - 1,) + ns[i+1:])))
            for i in xrange(len(ns)) if ns[i]]

def combine(*xss):
    ret = []
    for path in sum((paths(tree) for tree in gen(*(len(xs) for xs in xss))), []):
        stmts = []
        indexes = [0] * len(xss)
        for ixs in path:
            stmts.append(xss[ixs][indexes[ixs]])
            indexes[ixs] += 1
        ret.append(stmts)
    return ret

def walk(root, children, depth=0):
    print '{}{}'.format('  ' * depth, root)
    for c in children:
        walk(*c, depth=depth+1)

if __name__ == '__main__':
    r = combine('12', 'abc')
    for t in r:
        print t
    print len(r)
