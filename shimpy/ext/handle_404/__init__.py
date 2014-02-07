from shimpy.core import Extension, Block, NavBlock
from shimpy.core.context import context
from shimpy.core.utils import ReCheck

import os
import logging
import re

log = logging.getLogger(__name__)


class Handle404(Extension):
    priority = 99

    @staticmethod
    def _get_path(path):
        """
        >>> Handle404._get_path("/static/foo.txt")
        'foo.txt'
        >>> Handle404._get_path("/foo.txt")
        'foo.txt'
        >>> Handle404._get_path("/post/list")
        """
        rc = ReCheck()
        if rc.match("^(/static)?/([a-zA-Z0-9\.\-]+)$", path):
            return rc.group(2)
        return None

    @staticmethod
    def _get_disk_path(path):
        if path:
            theme = context.config.get("theme", "default")
            options = [
                os.path.abspath(os.path.join("shimpy", "theme", theme, path)),
                os.path.abspath(os.path.join("shimpy", "static", path)),
            ]
            existing = [p for p in options if os.path.isfile(p)]
            if existing:
                return existing[0]

    def onPageRequest(self, event, request):
        if context.page.mode != "page" or self.count_main(context) != 0:
            return  # something has already handled this request

        path = self._get_path(request.path)
        disk_path = self._get_disk_path(path)

        if disk_path:
            log.info("Serving static file: %s" % disk_path)
            context.page.set_expiration(600)
            context.page.mode = "data"
            context.page.data = file(disk_path).read()

            context.page.content_type = {
                "txt": "text/plain",
                "ico": "image/x-icon",
                "png": "image/png",
                "css": "text/css",
                "js": "application/javascript",
            }.get(disk_path.split(".")[-1], "text/plain")
        else:
            log.info("404 handler called for %r" % context.request.path)
            context.page.status = 404
            context.page.title = "404"
            context.page.heading = "404 - no handler found"
            context.page.add_block(NavBlock())
            context.page.add_block(Block("Explanation", "%r not found" % context.request.path))

    def count_main(self, context):
        return len([b for b in context.page.blocks if b.section == "main"])
