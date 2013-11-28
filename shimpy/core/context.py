from werkzeug.wrappers import Request
from webhelpers.html import literal

import threading


def _get_user(database, request):
    from shimpy.core.models import User
    return database.query(User).first()


class Cache(object):
    def __init__(self):
        self.hit_count = 0
        self.miss_count = 0


class Context(threading.local):
    """
    A class to carry round all the things that are important for a given request;
    per-request global variables, in a sense
    """
    def configure(self, server, database, environment):
        from shimpy.core.page import Page
        self.environment = environment
        self.server = server
        self.request = Request(environment)
        self.page = Page()
        self.database = database
        self.user = _get_user(self.database, self.request)
        self.config = server.config
        self.hard_config = server.hard_config
        self.cache = Cache()

        self._event_count = 0

    def get_debug_info(self):
        return literal("<br>Events sent: %d") % self._event_count


context = Context()
