from shimpy.core.block import Block
from shimpy.core.utils import make_link
import random
from webhelpers.html import literal


class Themelet(object):
    def display_error(self, page, status, title, message):
        page.status = status
        page.title = title
        page.header = title
        page.add_block(Block(title, message))
        # TODO: add nav block if not there already

    def display_permission_denied(self, page):
        self.display_error(page, 403, "Permission Denied", "You do not have permission to access this page")

    def build_thumb_html(self, image):
        # TODO
        return literal("""
            <a href="%(view_link)s" class="thumb shm-thumb" data-tags="%(tags)s" data-post-id="%(id)d">
                <img
                    id="thumb_%(id)d"
                    title="%(tip)s" alt="%(tip)s"
                    height="%(height)d" width="%(width)d"
                    src="%(thumb_link)s"
                />
            </a>
        """) % {
            "view_link": image.page_url,
            "thumb_link": image.thumb_url,
            "id": image.id,
            "tags": image.tags_plain_text,
            "tip": image.tooltip,
            "height": 192,
            "width": 192,
        }

    def display_paginator(self, page, base, query, page_number, total_pages):
        if total_pages == 0:
            total_pages = 1
        body = self.build_paginator(page_number, total_pages, base, query)
        page.add_block(Block(None, body, "main", 90, "paginator"))

    def gen_page_link(self, base_url, query, page, name):
        link = make_link(base_url + "/" + str(page), query)
        return literal("""<a href="%s">%s</a>""") % (link, name)

    def gen_page_link_block(self, base_url, query, page, current_page, name):
        link = self.gen_page_link(base_url, query, page, name)
        if page == current_page:
            link = literal("<b>%s</b>") % link
        return link

    def build_paginator(self, current_page, total_pages, base_url, query):
        next = current_page + 1
        prev = current_page - 1
        rand = random.randint(1, total_pages)

        at_start = (current_page <= 1 or total_pages <= 1)
        at_end = current_page >= total_pages

        first_html  = "First" if at_start else self.gen_page_link(base_url, query, 1, "First")
        prev_html   = "Prev"  if at_start else self.gen_page_link(base_url, query, prev, "Prev")
        random_html =                          self.gen_page_link(base_url, query, rand, "Random")
        next_html   = "Next"  if at_end   else self.gen_page_link(base_url, query, next, "Next")
        last_html   = "Last"  if at_end   else self.gen_page_link(base_url, query, total_pages, "Last")

        start = max(current_page - 5, 1)
        end = min(start+10, total_pages)

        pages = []
        for n in range(start, end):
            pages.append(self.gen_page_link_block(base_url, query, n, current_page, str(n)))

        return (
            literal(" | ").join([first_html, prev_html, random_html, next_html, last_html]) +
            literal("<br>") +
            literal(" | ").join(pages)
        )

