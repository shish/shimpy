from shimpy.core.page import Page


class Context(object):
    """
    A class to carry round all the things that are important for a given request;
    per-request global variables, in a sense
    """
    def __init__(self, server, environment):
        self.environment = environment
        #'REQUEST_METHOD': 'GET', 'PATH_INFO': '/post/view/2'
        #self.server = request.server
        #self.request = request
        self.page = Page()
        self.user = None
        self.database = server.database
        self.config = server.config

        self._event_count = 0
