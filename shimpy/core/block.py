import hashlib
from webhelpers.html import literal, HTML
from webhelpers.util import update_params


class Block(object):
    def __init__(self, header, body, section="main", position=0, class_=None):
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
    def __init__(self, force_pager=False):
        from shimpy.core.context import context
        request = context.request
        page_num = int(request.args.get("page", 1))

        nav = []

        if force_pager or "page" in request.args:
            nav.append(HTML.a("Prev", href=update_params(request.full_path, page=page_num-1)))

        nav.append(HTML.a("Index", href="/"))

        if force_pager or "page" in request.args:
            nav.append(HTML.a("Next", href=update_params(request.full_path, page=page_num+1)))

        Block.__init__(self, "Navigation", HTML.span(literal(" | ").join(nav)), "left", 0)
