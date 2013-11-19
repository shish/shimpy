from shimpy.core.page import Page
from shimpy.core.context import context
from shimpy.core.event import Event, PageRequestEvent
from shimpy.core.extension import Extension
from shimpy.core.database import connect, Session

from ConfigParser import SafeConfigParser

import logging

log = logging.getLogger(__name__)


class Shimpy(object):

    ###################################################################
    # Initialisation
    ###################################################################

    def __init__(self):
        self.hard_config = None
        self.extensions = []
        self.config = {}
        self.database = None

        self.load_hard_config()
        self.load_extensions()
        self.connect_db()
        self.load_config()
        self.load_themelets()

    def load_extensions(self):
        for name in self.hard_config.get("extensions", "list").split(","):
            log.info("Loading extension: %(extension)s", {"extension": name})

        from shimpy.ext.hello import Hello
        from shimpy.ext.view import ViewImage
        from shimpy.ext.handle_404 import Handle404
        from shimpy.ext.index import Index
        self.extensions = [
            #Hello(),
            ViewImage(),
            Index(),
            Handle404(),
        ]
        self.extensions = sorted(self.extensions)

    def load_hard_config(self):
        self.hard_config = SafeConfigParser()
        self.hard_config.read("config.ini")

    def connect_db(self):
        connect(self.hard_config)

    def load_config(self):
        self.config.update({})

    def load_themelets(self):
        pass

    ###################################################################
    # Page Serving
    ###################################################################

    def application(self, environment, start_response):
        sess = Session()
        context.configure(self, sess, environment)

        try:
            self.send_event(PageRequestEvent())
            context.page.render()
            Session.commit()
        except:
            Session.rollback()
            raise
        finally:
            Session.remove()

        start_response(str(context.page.status) + " OK?", context.page.http_headers)
        return [context.page.data]

    ###################################################################
    # Page Processing
    ###################################################################

    def send_event(self, event):
        log.info("Sending %(event)s", {"event": event.__class__.__name__})
        method_name = "on" + event.__class__.__name__.replace("Event", "")
        for ext in self.extensions:
            if hasattr(ext, method_name):
                getattr(ext, method_name)(event)

        context._event_count += 1


def main():
    logging.basicConfig(
        level=logging.INFO,
        #format="%(asctime)s %4.4(levelname)s %(name)s %(message)s"
        format="%(asctime)s %(levelname)4.4s %(name)s %(message)s"
    )
    s = Shimpy()
    try:
        log.info("Waiting for requests")
        from werkzeug.serving import run_simple
        run_simple(
            s.hard_config.get("server", "addr"), int(s.hard_config.get("server", "port")),
            s.application,
            use_reloader=True, use_debugger=True, extra_files=["config.ini"]
        )
    except KeyboardInterrupt:
        pass
