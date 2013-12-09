from werkzeug.wrappers import Request
from webhelpers.html import literal

import threading
from time import time
import logging

log = logging.getLogger(__name__)


def _get_user(database, request):
    from shimpy.core.models import User
    return database.query(User).first()


class Context(threading.local):
    """
    A class to carry round all the things that are important for a given request;
    per-request global variables, in a sense
    """
    def configure(self, server, database, environment):
        from shimpy.core.page import Page
        from shimpy.core.cache import Cache
        self.environment = environment
        self.server = server
        self.request = Request(environment)
        self.page = Page()
        self.database = database
        self.user = _get_user(self.database, self.request)
        self.config = server.config
        self.hard_config = server.hard_config
        self.cache = Cache()

        self._load_start = time()
        self._event_count = 0
        self._query_count = 0
        self._event_depth = 0

    def get_debug_info(self):
        from shimpy.core import __version__
        parts = [
            "Time: %.2f" % (time() - self._load_start),
            "Events sent: %d" % (self._event_count, ),
            "%d cache hits and %d misses" % (self.cache.hit_count, self.cache.miss_count),
            "Shimpy version %s" % (__version__, ),
        ]
        data = literal("<br>") + "; ".join(parts)
        log.debug("; ".join(parts))
        return data


context = Context()
