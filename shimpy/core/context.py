from werkzeug.wrappers import Request
from webhelpers.html import literal

import threading
from time import time
import logging
import structlog
import uuid

log = structlog.get_logger()


class Context(threading.local):
    """
    A class to carry round all the things that are important for a given request;
    per-request global variables, in a sense
    """
    def __init__(self):
        threading.local.__init__(self)
        self.environment = {}
        self.server = None
        self.request = Request({})
        self.remote_addr = None
        self.page = None
        self.send_event = None
        self.database = None
        self.user = None
        self.config = {}
        self.hard_config = None
        self.cache = None

        self._load_start = 0
        self._event_count = 0
        self._query_count = 0
        self._event_depth = 0

        log.new(user="<system>", addr=self.remote_addr, request_id=str(uuid.uuid4()))

    def configure(self, server, database, environment):
        from shimpy.core.page import Page
        from shimpy.core.cache import Cache
        from shimpy.core.models import User
        self.environment = environment
        self.server = server
        self.send_event = server.send_event
        self.request = Request(environment)
        self.remote_addr = self.request.access_route[0] if self.request.access_route else self.request.remote_addr
        self.page = Page()
        self.database = database
        self.user = User.by_request(self.request)
        self.config = server.config
        self.hard_config = server.hard_config
        self.cache = Cache()

        self._load_start = time()
        self._event_count = 0
        self._query_count = 0
        self._event_depth = 0

        log.new(user=self.user.username, addr=self.remote_addr, request_id=str(uuid.uuid4()))

    def get_debug_info(self):
        from shimpy.core import __version__
        parts = [
            "Time: %.2f" % (time() - self._load_start),
            "Events sent: %d" % (self._event_count, ),
            "%d cache hits and %d misses" % (self.cache.hit_count, self.cache.miss_count),
            "Shimpy version %s" % (__version__, ),
        ]
        data = literal("<br>") + "; ".join(parts)
        log.debug("Render stats", stats="; ".join(parts))
        return data


context = Context()
