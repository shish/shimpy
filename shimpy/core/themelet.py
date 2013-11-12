from shimpy.core.block import Block


class Themelet(object):
    def display_error(self, page, status, header, body):
        page.status = status
        page.header = header
        page.add_block(Block(header, body))

    def display_permission_denied(self):
        self.display_error(403, "Permission Denied", "You do not have permission to access this page")

    def build_thumb_html(self, image):
        pass

    def display_paginator(self, page, base, query, page_number, total_pages):
        pass

    def gen_page_link(self, base_url, query, page, name):
        pass

    def gen_page_link_block(self, base_url, query, page, current_page, name):
        pass

    def build_paginator(self, current_page, total_pages, base_url, query):
        pass

