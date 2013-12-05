import hashlib
from webhelpers.html import literal, HTML


class Block(object):
    def __init__(self, header, body, section="main", position="0", class_=None):
        self.header = header
        self.body = body
        self.section = section
        self.position = position
        self.class_ = class_

        if header:
            self._id = header.replace(" ", "_")
        else:
            self._id = hashlib.md5(body).hexdigest()

    def __html__(self, hidable=False):
        if hidable:
            toggler = "shm-toggler"
        else:
            toggler = ""

        if self.header:
            header = literal("""<h3 data-toggle-sel="%s" class="%s">%s</h3>""") % (self._id, toggler, self.header)
        else:
            header = ""

        # TODO don't include block body if empty
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
        body = HTML.a("/", href="%s")  # TODO: get main page
        Block.__init__(self, "Navigation", body, "left", 0)
