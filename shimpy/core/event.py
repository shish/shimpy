
class Event(object):
    def __init__(self, context):
        self.context = context

class PageRequestEvent(Event):
    def page_matches(self, page):
        pass

    def get_arg(self, idx):
        pass
