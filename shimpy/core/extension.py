
class Extension(object):
    priority = 50

    def __init__(self):
        self.theme = None

    def __cmp__(self, other):
        return cmp(self.priority, other.priority)
