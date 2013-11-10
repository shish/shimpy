from shimpy.core.page import Page
from shimpy.core.context import Context
from shimpy.core.event import Event, PageRequestEvent
from shimpy.core.extension import Extension
from shimpy.core.database import connect, Session

from ConfigParser import SafeConfigParser

import BaseHTTPServer
import logging

log = logging.getLogger(__name__)


class ShimpyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        ctx = Context(self)

        try:
            try:
                ctx.database = Session()
                self.server.send_event(PageRequestEvent(ctx))
                Session.commit()
            except:
                Session.rollback()
                raise
            finally:
                Session.remove()
        except Exception as e:
            ctx.page.status = 500
            ctx.page.headers = []
            ctx.page.data = str(e)

        self.send_response(ctx.page.status)
        for k, v in ctx.page.headers:
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(ctx.page.data)


class Shimpy(BaseHTTPServer.HTTPServer):
    def __init__(self):
        BaseHTTPServer.HTTPServer.__init__(self, ("0.0.0.0", 8080), ShimpyHandler)

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
            print "Loading extension: %s" % name

        from shimpy.ext.hello import Hello
        self.extensions = [Hello(), ]

    def load_hard_config(self):
        self.hard_config = SafeConfigParser()
        self.hard_config.read("config.ini")

    def connect_db(self):
        connect(self.hard_config)

    def load_config(self):
        self.config.update({})

    def load_themelets(self):
        pass

    def send_event(self, event):
        print "Sending %s" % event.__class__.__name__
        method_name = "on" + event.__class__.__name__.replace("Event", "")
        for ext in self.extensions:
            if hasattr(ext, method_name):
                getattr(ext, method_name)(event)

        event.context._event_count += 1


def main():
    logging.basicConfig(
        level=logging.INFO,
        #format="%(asctime)s %4.4(levelname)s %(name)s %(message)s"
        format="%(asctime)s %(name)s %(message)s"
    )
    s = Shimpy()
    try:
        log.info("Waiting for requests")
        s.serve_forever()
    except KeyboardInterrupt:
        pass
    s.server_close()
