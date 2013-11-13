from shimpy.core.page import Page
from shimpy.core.models import User

from werkzeug.wrappers import Request


def _get_user(database, request):
    return database.query(User).first()


class Context(object):
    """
    A class to carry round all the things that are important for a given request;
    per-request global variables, in a sense
    """
    def __init__(self, server, database, environment):
        self.environment = environment
        self.server = server
        self.request = Request(environment)
        self.page = Page()
        self.database = database
        self.user = _get_user(self.database, self.request)
        self.config = server.config
        self.hard_config = server.hard_config

        self._event_count = 0
