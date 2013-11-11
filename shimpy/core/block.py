import hashlib
from webhelpers.html import literal

class Block(object):
    def __init__(self, header, body, section="main", position="0"):
        self.header = header
        self.body = body
        self.section = section
        self.position = position

        if header:
            self._id = header.replace(" ", "_")
        else:
            self._id = hashlib.md5(body).hexdigest()

    def __html__(self):
        if self.header:
            header = literal("""<h3 data-toggle-sel="%s">%s</h3>""") % (self._id, self.header)
        else:
            header = ""
        return literal("""
            <section id="%(id)s">
                %(header)s
                <div class="blockbody">%(body)s</div>
            </section>
        """) % {
            "id": self._id,
            "header": header,
            "body": self.body,
        }

    def __cmp__(self, other):
        return cmp(self.position, other.position)


class NavBlock(Block):
    def __init__(self):
        body = literal("""<a href="%s">Index</a>""") % "/"  # TODO: get main page
        Block.__init__(self, "Navigation", body, "left", 0)
