from shimpy.core.page import Page
from shimpy.core.context import context
from shimpy.core.event import Event, PageRequestEvent, InitExtEvent
from shimpy.core.extension import Extension
from shimpy.core.database import connect, Session

from ConfigParser import SafeConfigParser

import logging
import time
from pkg_resources import iter_entry_points

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
        self.extensions = []
        for entry_point in iter_entry_points("shimpy.extensions"):
            log.info("Loading extension: %(extension)s", {"extension": entry_point.name})
            self.extensions.append(entry_point.load()())
        #for name in self.hard_config.get("extensions", "list").split(","):
        #    log.info("Loading extension: %(extension)s", {"extension": name})
        self.extensions = sorted(self.extensions)

    def load_hard_config(self):
        self.hard_config = SafeConfigParser()
        self.hard_config.read("config.ini")

    def connect_db(self):
        connect(self.hard_config)

    def load_config(self):
        self.config.update({})

        section = "forced_config"
        for option in self.hard_config.options(section):
            self.config[option] = self.hard_config.get(section, option)

    def load_themelets(self):
        pass

    ###################################################################
    # Page Serving
    ###################################################################

    def application(self, environment, start_response):
        sess = Session()
        context.configure(self, sess, environment)

        try:
            self.send_event(InitExtEvent())
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
        context._event_depth += 1

        log.info("Sending %(event)s", {"event": event.__class__.__name__})
        method_name = "on" + event.__class__.__name__.replace("Event", "")
        for ext in self.extensions:
            t2 = time.time()
            if hasattr(ext, method_name):
                getattr(ext, method_name)(event)
            t3 = time.time()
            if t3 - t2 > 0.1:
                print "%-25s %-25s %-5.3f" % (event.__class__.__name__, ext.__class__.__name__, t3 - t2)
        log.info("Ending %(event)s", {"event": event.__class__.__name__})

        context._event_count += 1
        context._event_depth -= 1


def main():
    logging.basicConfig(
        level=logging.INFO,
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
