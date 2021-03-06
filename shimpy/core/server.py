from shimpy.core.page import Page
from shimpy.core.context import context
from shimpy.core.config import Config
from shimpy.core.event import Event, PageRequestEvent, InitExtEvent, CommandEvent
from shimpy.core.extension import Extension
from shimpy.core.database import connect, Session

from ConfigParser import SafeConfigParser

import logging
import structlog
import time
import sys
from pkg_resources import iter_entry_points

log = structlog.get_logger()


class Shimpy(object):

    ###################################################################
    # Initialisation
    ###################################################################

    def __init__(self):
        self.hard_config = None
        self.extensions = []
        self.config = Config()
        self.database = None

        self.load_hard_config()
        self.load_extensions()
        self.connect_db()
        self.load_config()
        self.load_themelets()
        self.init_extensions()

    def load_extensions(self):
        self.extensions = []
        for entry_point in iter_entry_points("shimpy.extensions"):
            log.info("Loading extension", extension=entry_point.name)
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
#        sess = Session()
#        for row in sess.execute("SELECT name, value FROM config"):
#            try:
#                self.config[row["name"]] = int(row["value"])
#            except:
#                self.config[row["name"]] = row["value"]
#        Session.remove()

        section = "forced_config"
        for option in self.hard_config.options(section):
            self.config[option] = self.hard_config.get(section, option)

    def load_themelets(self):
        pass

    def init_extensions(self):
        sess = Session()
        context.configure(self, sess, {})
        self.send_event(InitExtEvent())

    ###################################################################
    # Page Serving
    ###################################################################

    def application(self, environment, start_response):
        sess = Session()
        context.configure(self, sess, environment)

        try:
            log.info("Page request", path=context.request.path)
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

        #log.debug("Sending event", eventclass=event.__class__.__name__)
        method_name = "on" + event.__class__.__name__.replace("Event", "")
        for ext in self.extensions:
            t2 = time.time()
            if hasattr(ext, method_name):
                on = getattr(ext, method_name)
                onc = on.im_func.func_code
                args = []
                for k in onc.co_varnames[2:onc.co_argcount]:  # "self, event" are always first
                    if k in context.__dict__:
                        args.append(context.__dict__[k])
                on(event, *args)
            t3 = time.time()
            if t3 - t2 > 0.5:
                log.warning("Slow event", eventclass=event.__class__.__name__, ext=ext.__class__.__name__, time=t3 - t2)
        #log.debug("Ending event", eventclass=event.__class__.__name__)

        context._event_count += 1
        context._event_depth -= 1

        return event


def main(args=sys.argv):
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        filename="app.log",
        #format="%(asctime)19.19s %(levelname)4.4s %(name)s %(message)s"
    )
    structlog.configure(
        processors=[
            structlog.processors.KeyValueRenderer(
                key_order=['request_id', 'user', 'addr', 'event'],
            ),
            #structlog.processors.StackInfoRenderer(),
            #structlog.processors.format_exc_info,
            #structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=structlog.threadlocal.wrap_dict(dict),
        cache_logger_on_first_use=True,
    )

    s = Shimpy()
    if len(args) > 1:
        args = [a.decode(sys.stdin.encoding) for a in args]
        log.info("Sending command event", command=args[1:])
        s.send_event(CommandEvent(args[1:]))
    else:
        try:
            log.info("Waiting for requests")
            from werkzeug.serving import run_simple
            logging.getLogger("werkzeug").setLevel(logging.WARN)
            hc = s.hard_config
            run_simple(
                hc.get("server", "addr"), int(hc.get("server", "port")),
                s.application,
                use_reloader=int(hc.get("server", "reload")),
                use_debugger=int(hc.get("server", "debug")),
                extra_files=["config.ini"]
            )
        except KeyboardInterrupt:
            pass

