from mako.template import Template
from webhelpers.html import literal
from glob import glob
from datetime import datetime, timedelta

from shimpy.core import __version__
from shimpy.core.utils import SparseList
from shimpy.core.context import context


class Page(object):
    def __init__(self):
        self.mode = "page"

        # global
        self.status = 200
        self.http_headers = SparseList()
        self.content_type = "text/html; charset=utf-8"

        # mode = data
        self.data = ""
        self.filename = None

        # mode = redirect
        self.redirect = None

        # mode = page
        self.title = ""
        self.heading = ""
        self.subheading = ""
        self.quicknav = ""
        self.html_headers = SparseList()
        self.blocks = []

    # global
    def add_http_header(self, key, value, position=50):
        self.http_headers[position] = (key, value)

    def set_expiration(self, seconds):
        if seconds > 0:
            self.add_http_header("Cache-control", "public, max-age=%d" % seconds)
        else:
            self.add_http_header("Cache-control", "no-cache")
        self.add_http_header("Expires", (datetime.now() + timedelta(seconds=seconds)).strftime("%a, %d %b %Y %H:%M:%S %Z"))

    # mode = page
    def add_html_header(self, data, position=50):
        self.html_headers[position] = data

    def delete_all_html_headers(self):
        self.html_headers = SparseList()

    def add_block(self, block):
        self.blocks.append(block)

    def render(self):
        self.add_http_header("Content-type", self.content_type)
        self.add_http_header("X-Powered-By", "Shimpy %s" % __version__)

        if self.mode == "page":
            if context.hard_config.get("cache", "http") == "on":
                self.add_http_header("Vary", "Cookie, Accept-Encoding")
                if context.user.is_anonymous() and context.request.method == "GET":
                    self.set_expiration(600)
                else:
                    self.set_expiration(-1)

            self.blocks = sorted(self.blocks)
            self.add_auto_html_headers()

            template = Template(filename='shimpy/theme/%s/layout.mako' % context.config.get("theme", "default"))
            self.data = template.render(ctx=context, page=self)
            self.mode = "data"
            self.filename = None

        if self.mode == "data":
            self.add_http_header("Content-length", len(self.data))
            if self.filename:
                self.add_http_header("Content-Disposition", "attachment; filename=" + self.filename)

        elif self.mode == "redirect":
            self.status = 302
            self.add_http_header("Location", self.redirect)
            self.data = literal('You should be redirected to <a href="%s">%s</a>') % (self.redirect, self.redirect)

        else:
            self.data = "Invalid page mode: %r" % self.mode

        if type(self.data) != bytes:
            self.data = bytes(self.data)

    def add_auto_html_headers(self):
        # 404/static handler will map these to themes/foo/bar.ico or lib/static/bar.ico
        self.add_html_header(literal("<link rel='icon' type='image/x-icon' href='/favicon.ico'>"))
        self.add_html_header(literal("<link rel='apple-touch-icon' href='/apple-touch-icon.png'>"))

        theme = context.config.get("theme", "default")

        # TODO: concatenate files
        for css in (
            glob("shimpy/static/*.css") +
            glob("shimpy/ext/*/style.css") +
            glob("shimpy/theme/%s/*.css" % theme)
        ):
            css = css.replace("shimpy/static/", "")
            css = css.replace("shimpy/theme/%s/" % theme, "")
            self.add_html_header(literal("<link rel='stylesheet' href='/static/%s' type='text/css'>") % css)

        for js in (
            glob("shimpy/static/*.js") +
            glob("shimpy/ext/*/script.css") +
            glob("shimpy/theme/%s/script.js" % theme)
        ):
            self.add_html_header(literal("<script src='/static/%s'></script>") % js.replace("shimpy/static", ""))
