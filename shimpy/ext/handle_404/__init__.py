from shimpy.core import Extension, Block, NavBlock

import os
import logging
import re

log = logging.getLogger(__name__)


class Handle404(Extension):
    priority = 99

    def onPageRequest(self, event):
        ctx = event.context

        # TODO: handle /foo.bar if /static/foo.bar exists (or theme'd override)
        if re.match("^/[a-zA-Z0-9\.\-]+$", ctx.request.path):
            options = [
                os.path.abspath(os.path.join("shimpy", "theme", "./" + ctx.request.path)),
                os.path.abspath(os.path.join("shimpy", "static", "./" + ctx.request.path)),
            ]
            existing = [path for path in options if os.path.isfile(path)]
            if existing:
                disk_path = existing[0]
                log.info("Serving static file: %s" % disk_path)
                ctx.page.set_expiration(600)
                ctx.page.mode = "data"
                ctx.page.data = file(disk_path).read()

                ctx.page.content_type = {
                    "txt": "text/plain",
                    "ico": "image/x-icon",
                    "png": "image/png",
                    "css": "text/css",
                    "js": "application/javascript",
                }.get(disk_path.split(".")[-1], "text/plain")

        if ctx.page.mode == "page" and self.count_main(ctx) == 0:
            log.info("404 handler called for %r" % ctx.request.path)
            ctx.page.status = 404
            ctx.page.title = "404"
            ctx.page.heading = "404 - no handler found"
            ctx.page.add_block(NavBlock())
            ctx.page.add_block(Block("Explanation", "%r not found" % ctx.request.path))

    def count_main(self, ctx):
        return len([b for b in ctx.page.blocks if b.section == "main"])
