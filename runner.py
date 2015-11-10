from collections import deque
import copy
import itertools
import random
import re

class Semaphore(object):

    def __init__(self, count):
        self.count = count
        self.wait_queue = deque()

    def P(self):
        self.count -= 1
        if self.count < 0:
            thread = self.runner.current_thread
            self.wait_queue.append(thread)
            thread.blocked = True
    wait = P
    acquire = P

    def V(self):
        self.count += 1
        try:
            thread = self.wait_queue.popleft()
            thread.blocked = False
        except IndexError:
            pass
    signal = V
    release = V

    def __repr__(self):
        return '<Sem {}>'.format(self.count)

class Statement(object):

    def __init__(self, line, thread):
        self.line = line
        self.thread = thread

    def _split(self):
        return re.split(self.PATTERN, self.line)[1:-1]

    def env(self):
        return self.thread.locals, self.thread.globals

    def __repr__(self):
        return '{:4} {:10}: "{}"'.format(
                self.thread.name, self.__class__.__name__, self.line)

class NopeStmt(Statement):

    PATTERN = re.compile(r'\s*(\w+)')

    def __init__(self, line, thread):
        super(NopeStmt, self).__init__(line, thread)
        self.name = self._split()

    def execute(self):
        return self.line

class AssignStmt(Statement):

    PATTERN = re.compile(r'\s*(\w+)\s*=\s*(.*)\s*')

    def __init__(self, line, thread):
        super(AssignStmt, self).__init__(line, thread)
        self.name, self.expr = self._split()

    def __repr__(self):
        return super(AssignStmt, self).__repr__() + ' (var: {}, expr: {})'.format(
                self.name, self.expr)

    def execute(self):
        locals, globals = self.env()
        d = globals if self.name in globals else locals
        v = eval(self.expr, dict(globals), dict(locals))
        d[self.name] = v
        return self.line + ' # {}'.format(v)

class MethodStmt(Statement):

    PATTERN = re.compile(r'\s*(\w+)\.(\w+)\(.*\)\s*')

    def __init__(self, line, thread):
        super(MethodStmt, self).__init__(line, thread)
        self.obj_name, self.method_name = self._split()

    def __repr__(self):
        return super(MethodStmt, self).__repr__() + ' (obj: {}, method: {})'.format(
                self.obj_name, self.method_name)

    def execute(self):
        locals, globals = self.env()
        obj = globals[self.obj_name]
        f = getattr(obj, self.method_name)
        f()
        return self.line + ' # {}'.format(obj)

class DuckThread(object):

    def __init__(self, locals={}, globals=globals()):
        self.locals = locals
        self.globals = globals
        self.name = 'Duck'

    def __repr__(self):
        return '<DuckThread> with\n\tlocals: {}\n\tglobals: {}'.format(
                self.locals, self.globals)

def statement(line, thread=None):
    for stmt_cls in (AssignStmt, MethodStmt, NopeStmt):
        if re.match(stmt_cls.PATTERN, line):
            return stmt_cls(line, thread)

class Thread(object):

    def __init__(self, lines, globals):
        lines = [line.strip() for line in lines]
        lines = filter(bool, lines)
        self.name = lines[0]
        self.globals = globals
        self.locals = {}
        self.stmts = [statement(line, self) for line in lines[1:]]
        if self.stmts:
            self._blocked = False
            self.finished = False
            self.ready = True
        else:
            self._blocked = True
            self.finished = True
            self.ready = False
        self.i_cur_stmt = 0

    @property
    def steppable(self):
        return not self.blocked and not self.finished

    @property
    def blocked(self):
        return self._blocked

    @blocked.setter
    def blocked(self, val):
        self._blocked = val
        self.ready = not val

    def reset(self):
        self.i_cur_stmt = 0
        self.blocked = False
        self.finished = False

    def step(self):
        if self.blocked or self.finished:
            raise Exception('Thread {} is {}'.format(
                self.name, 'blocked' if self.blocked else 'finished'))
        stmt = self.stmts[self.i_cur_stmt]
        self.i_cur_stmt += 1
        if self.i_cur_stmt == len(self.stmts):
            self.finished = True
        return stmt.execute()

    def __repr__(self):
        s = 'Thread({})'.format(self.name)
        s += '\n\tlocals: {}'.format(self.locals)
        s += '\n\tglobals: {}'.format(self.globals)
        return s

class Runner(object):

    def __init__(self, fname):
        if '\n' in fname:
            lines = fname.split('\n')
        else:
            lines = open(fname).readlines()
        lines = (l.strip() for l in lines)
        lines = (l for l in lines if not l.startswith('#'))
        parts = [list(filter(bool, g)) for k, g in itertools.groupby(lines, bool) if k]
        codes, definitions = parts[:-1], parts[-1]
        globals = dict(self.variable(d) for d in definitions)
        self.globals = globals
        self.threads = [Thread(code, self.globals) for code in codes]
        self.stmt = None
        self.thread = None
        self.self = self.backup()

    def restore(self, backup=None):
        if backup is None:
            backup = self.self
        self.__dict__ = backup.__dict__
        self.self = backup

    def backup(self):
        return copy.deepcopy(self)

    def stepped(self, index):
        self.current_thread = self.threads[index]
        self.thread = self.current_thread
        self.stmt = self.thread.step()
        return self

    def run(self):
        ret = []
        self.restore()
        while True:
            threads = [t for t in self.threads if t.steppable]
            if not threads:
                break
            thread = random.choice(threads)
            self.current_thread = thread
            result = thread.step()
            ret.append((thread, result, self.backup()))
        return ret

    def run_all_paths(self):

        def traverse(root, children):
            indexes = [i for i, t in enumerate(root.threads) if t.steppable]
            children[:] = [(root.backup().stepped(i), []) for i in indexes]
            for node in children:
                traverse(*node)
            return root, children

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

        return Paths(Path(snapshots) for snapshots in paths(traverse(self.backup(), [])))

    def variable(self, v):
        name, val = (t.strip() for t in v.split('='))
        val = eval(val)
        if isinstance(val, Semaphore):
            val.runner = self
        return name, val

class Path(object):

    def __init__(self, snapshots):
        self.snapshots = snapshots
        self.last = self.snapshots[-1]
        self.finished = all(t.finished for t in self.last.threads)
        self.stmts = [snap.stmt for snap in self.snapshots[1:]]

    def __call__(self, expr):
        op = '<' if '<' in expr else '>'
        expect = [t.strip() for t in expr.split(op)]
        actual = [t for t in self.stmts if t in expect]
        if op == '>':
            actual = list(reversed(actual))
        return actual == expect

    def __getitem__(self, key):
        return self.last.globals[key]

    def val(self, *keys):
        if not keys:
            keys = self.last.globals.keys()
        return tuple(self[key] for key in keys)

    def show(self):
        snap = self.snapshots[0]
        indexes = dict(zip((t.name for t in snap.threads), itertools.count()))
        snapshots = self.snapshots[1:]
        width = 80 / len(snap.threads)
        print ''.join('{:<{}}'.format('~~~~~~ ' + t.name, width)
                for t in snap.threads).strip()
        for r in snapshots:
            index = indexes[r.thread.name]
            print '{}{:}'.format(' ' * index * width, r.stmt)
        return self

class Paths(object):

    def __init__(self, paths):
        self.paths = list(paths)
        self.finished = [path.finished for path in self.paths]

    def __len__(self):
        return len(self.paths)

    def __call__(self, expr):
        return tuple(path(expr) for path in self.paths)

    def __getitem__(self, key):
        return tuple(path[key] for path in self.paths)

    def val(self, *keys):
        return tuple(path.val(*keys) for path in self.paths)

    def show(self, pause=False):
        for i, path in enumerate(self.paths):
            path.show()
            print '=' * 70 + '{}/{}'.format(i + 1, len(self))
            if pause and i != len(self) - 1:
                raw_input()
        return self

def run(fname):
    return Runner(fname).run_all_paths()

if __name__ == '__main__':
    runner = Runner('t.txt')
    paths = runner.run_all_paths()
    #print len(paths)
    #print all(paths.finished)
    #print all(paths('a1 > b1'))
    paths.show()
