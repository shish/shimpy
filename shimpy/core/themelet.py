from shimpy.core.block import Block


class Themelet(object):
    def display_error(self, page, status, title, message):
        page.status = status
        page.title = title
        page.header = title
        page.add_block(Block(title, message))
        # TODO: add nav block if not there already

    def display_permission_denied(self, page):
        self.display_error(page, 403, "Permission Denied", "You do not have permission to access this page")

    def build_thumb_html(self, context, image):
        # TODO
        pass

    def display_paginator(self, page, base, query, page_number, total_pages):
        if total_pages == 0:
            total_pages = 1
        body = self.build_paginator(page_number, total_pages, base, query)
        page.add_block(Block(None, body, "main", 90, "paginator"))

    def gen_page_link(self, base_url, query, page, name):
        link = make_link(base_url + "/" + page, query)
        return literal("""<a href="%s">%s</a>""") % (link, name)

    def gen_page_link_block(self, base_url, query, page, current_page, name):
        link = self.gen_page_link(base_url, query, page, name)
        if page == current_page:
            link = literal("<b>%s</b>") % link
        return link

    def build_paginator(self, current_page, total_pages, base_url, query):
        # TODO
        pass

