import threading
import Queue
import random

class Tester(object):

    def before(self, *stmts):
        pass

    def group(self, *stmts):
        pass

    def add(self, *funcs):
        self.funcs = funcs

    def run(self, nPass=1):
        for iPass in range(nPass):
            self.q = Queue.Queue()
            threads = [threading.Thread(target=f) for f in self.funcs]
            random.shuffle(threads)
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            while True:
                try:
                    stmt = self.q.get(False)
                    print stmt
                except Queue.Empty:
                    break
            print '=' * 10 + 'Passed {}/{}'.format(iPass + 1, nPass)

tester = Tester()

def put(stmt):
    tester.q.put(stmt)
