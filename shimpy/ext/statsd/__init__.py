from shimpy.core import Extension
from shimpy.core.context import context

import socket
from time import time


def dstat(name, val):
    context._stats["shimpy.%s" % name] = val


class StatsD(Extension):
    """
    Name: StatsD Interface
    Author: Shish <webmaster@shishnet.org>
    License: GPLv2
    Visibility: admin
    Description: Sends Shimmie stats to a StatsD server
    Documentation:
        in config.ini to set the host:
        [statsd]
        host = my.server.com:8125
    """
    priority = 99

    def __init__(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __stats(self, type_):
        page_time = time() - context._load_start
        context._stats["shimpy.%s.hits" % type_] = "1|c"
        context._stats["shimpy.%s.time" % type_] = "%f|ms" % page_time
        #context._stats["shimpy.%s.memory" % type_] = "1|c"
        #context._stats["shimpy.%s.files" % type_] = "1|c"
        context._stats["shimpy.%s.queries" % type_] = "%d|c" % context._query_count
        context._stats["shimpy.%s.events" % type_] = "%d|c" % context._event_count
        context._stats["shimpy.%s.cache-hits" % type_] = "%d|c" % context.cache.hit_count
        context._stats["shimpy.%s.cache-misses" % type_] = "%d|c" % context.cache.miss_count

    def __send_stats(self, data, sample_rate):
        try:
            host = context.hard_config.get("statsd", "host")
        except Exception:
            return

        if not host:
            return

        sampled_data = {}
        if sample_rate < 1:
            for stat, value in data.items():
                if random() <= sample_rate:
                    sampled_data[stat] = "%s|@%f" % (value, sample_rate)
        else:
            sample_data = data

        if not sample_data:
            return

        try:
            parts = host.split(":")
            addr = (parts[0], int(parts[1]))
            packet = "\n".join("%s:%s" (stat, value) for stat, value in sample_data.items())
            self.socket.sendto(packet, addr)
        except Exception:
            pass

    def onInitExt(self, event):
        context._stats = {}

    def onPageRequest(self, event):
        self.__stats("overall")

        if event.page_matches("post/list"):
            self.__stats("post/list")
        elif event.page_matches("post/view"):
            self.__stats("post/view")
        elif event.page_matches("user"):
            self.__stats("user")
        elif event.page_matches("upload"):
            self.__stats("upload")
        elif event.page_matches("rss"):
            self.__stats("rss")
        else:
            self.__stats("other")

        self.__send_stats(context._stats, 1.0)

    def onUserCreation(self, event):
        dstat("shimpy.events.user_creations", "1|c")

    def onDataUpload(self, event):
        dstat("shimpy.events.uploads", "1|c")

    def onCommentPosting(self, event):
        dstat("shimpy.events.comments", "1|c")

    def onImageInfoSet(self, event):
        dstat("shimpy.events.info-sets", "1|c")
