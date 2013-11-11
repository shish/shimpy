from shimpy.theme.layout import Layout
from webhelpers.html import literal


class Page(object):
    def __init__(self):
        self.status = 200
        self.http_headers = []

        self.mode = "page"

        # mode = page
        self.html_headers = []
        self.title = ""
        self.heading = ""
        self.blocks = []

        # mode = data
        self.content_type = "text/html; charset=utf-8"
        self.filename = None
        self.data = ""

        # mode = redirect
        self.redirect = None

    def add_html_header(self, data):
        self.html_headers.append(data)

    def add_http_header(self, key, value):
        self.http_headers.append((key, value))

    def add_block(self, block):
        self.blocks.append(block)

    def render(self, context):
        self.add_http_header("Content-type", self.content_type)
        self.add_http_header("X-Powered-By", "Shimpy Alpha")
        
        if self.mode == "page":
            # TODO: caching headers
            self.blocks = sorted(self.blocks)
            self.add_auto_html_headers()
            self.data = Layout().display_page(self, context)
            self.mode = "data"
            self.filename = None

        if self.mode == "data":
            self.add_http_header("Content-length", len(self.data))
            if self.filename:
                self.add_http_header("Content-Disposition", "attachment; filename=" + self.filename)

        elif self.mode == "redirect":
            self.add_http_header("Location", self.redirect)
            self.data = literal('You should be redirected to <a href="%s">%s</a>') % (self.redirect, self.redirect)

        else:
            self.data = "Invalid page mode: %r" % self.mode

    def add_auto_html_headers(self):
        pass
