from shimpy.core import Extension, Block, NavBlock
from shimpy.core.context import context

import os
import logging
import re

log = logging.getLogger(__name__)


class Handle404(Extension):
    priority = 99

    def onPageRequest(self, event):
        # TODO: handle /foo.bar if /static/foo.bar exists (or theme'd override)
        if re.match("^/[a-zA-Z0-9\.\-]+$", context.request.path):
            theme = context.config.get("theme", "default")
            options = [
                os.path.abspath(os.path.join("shimpy", "theme", theme, "./" + context.request.path)),
                os.path.abspath(os.path.join("shimpy", "static", "./" + context.request.path)),
            ]
            existing = [path for path in options if os.path.isfile(path)]
            if existing:
                disk_path = existing[0]
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

        if context.page.mode == "page" and self.count_main(context) == 0:
            log.info("404 handler called for %r" % context.request.path)
            context.page.status = 404
            context.page.title = "404"
            context.page.heading = "404 - no handler found"
            context.page.add_block(NavBlock())
            context.page.add_block(Block("Explanation", "%r not found" % context.request.path))

    def count_main(self, context):
        return len([b for b in context.page.blocks if b.section == "main"])
