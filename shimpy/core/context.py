from shimpy.core.page import Page


class Context(object):
    def __init__(self, request):
        self.server = request.server
        self.request = request
        self.page = Page()
        self.user = None
        self.database = request.server.database
        self.config = request.server.config

        self._event_count = 0
