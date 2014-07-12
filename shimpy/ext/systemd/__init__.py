from shimpy.core import Extension
from shimpy.core.context import context

import structlog
import ctypes
import os

log = structlog.get_logger()


class Systemd(Extension):
    """
    Name: Systemd Integration
    Author: Shish <webmaster@shishnet.org>
    License: GPLv2
    Visibility: admin
    Description: Lets systemd know that the service is alive each time a page is requested
    """
    priority = 99

    def onInitExt(self, event):
        self.__sd = None
        try:
            self.__sd = ctypes.CDLL(ctypes.util.find_library("systemd-daemon"))
            self.__sd.sd_notify(0, "READY=1")
            self.__sd.sd_notify(0, "MAINPID=%d" % os.getpid())  # we aren't the main pid if we're in debug-reloader mode
            self.__sd.sd_notify(0, "STATUS=Waiting for requests")
            log.info("Let systemd know that we're ready")
        except Exception as e:
            log.error("Error loading systemd library", exception=e)

    def onPageRequest(self, event, request):
        if self.__sd:
            self.__sd.sd_notify(0, "WATCHDOG=1")
            self.__sd.sd_notify(0, "STATUS=Got a request for %s" % request.path.encode("ascii", "ignore"))
