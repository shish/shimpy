
class SparseList(object):
    def __init__(self):
        self.values = {}

    def insert(self, pos, val):
        pos = float(pos)
        while True:
            if pos in self.values:
                pos = pos + (1.0/128.0)
            self.values[pos] = val
