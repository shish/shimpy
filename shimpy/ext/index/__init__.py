from shimpy.core import Extension, Block, NavBlock, Themelet, Event
from shimpy.core.models import Image
from shimpy.core.utils import SparseList

import os
import logging
import re
from webhelpers.html import literal

log = logging.getLogger(__name__)


class SearchTermParseEvent(Event):
    def __init__(self, context, term):
        self.context = context
        self.term = term
        self.querylets = []

    def is_querylet_set(self):
        return len(self.querylets) > 0

    def get_querylest(self):
        return self.querylets

    def add_querylet(self, q):
        self.querylets.append(q)


class SearchTermParseException(Exception):
    pass


class PostListBuildingEvent(Event):
    def __init__(self, context, search_terms):
        self.context = context
        self.search_terms = search_terms
        self.parts = SparseList()

    def add_control(self, html, position=50):
        self.parts.insert(position, html)


class IndexTheme(Themelet):
    def set_page(self, page, page_number, total_pages, search_terms):
        self.page_number = page_number
        self.total_pages = total_pages
        self.search_terms = search_terms

    def display_intro(self, page):
        text = literal("""
<div style='text-align: left;'>
<p>The first thing you'll probably want to do is create a new account; note
that the first account you create will by default be marked as the board's
administrator, and any further accounts will be regular users.

<p>Once logged in you can play with the settings, install extra features,
and of course start organising your images :-)

<p>This message will go away once your first image is uploaded~
</div>
""")
        page.title = "Welcome to Shimpy"
        page.heading = "Welcome to Shimpy"
        page.add_block(Block("Installation Succeeded!", text))

    def display_page(self, page, images):
        config = None

        if not self.search_terms:
            query = None
            page_title = config.get_string("title")

        else:
            search_string = " ".join(self.search_terms)  # TODO: Tag.join()?
            page_title = search_string

            if images:
                page.subheading = "Page %d / %d" % (self.page_number, self.total_pages)

        page.title = page_title
        page.heading = page_title
        page.add_block(Block("Navigation", self.build_navigation(), "left", 0))

        if images:
            page.add_block(Block("Images", self.build_table(images, ("#search="+query) if query else None), "main", 10, "image-list"))
            self.display_paginatior(page, "post/list/"+query if query else "post/list", null, self.page_number, self.total_pages)
        else:
            self.display_error(page, 404, "No Images Found", "No images were found to match the search criteria")

    def display_admin_block(self, page, parts):
        page.add_block(Block("List Controls", literal("<br>").join(parts), "left", 50))

    def build_navigation(self):
        prev = self.page_number - 1
        next = self.page_number + 1

        tags = " ".join(self.search_terms)  # TODO: Tag.join()?
        # TODO

        return "Nav stuff"

    def build_table(self, images, query):
        table = literal("""<div class="shm-image-list" data-query="%s">""") % query
        for image in images:
            table += self.build_thumb_html(image)
        table += literal( "</table>")
        return table


class Index(Extension):
    def __init__(self):
        self.theme = IndexTheme()

    def onInitExt(self, event):
        # event.context.config.set_default_int("index_images", 24)
        # event.context.config.set_default_bool("index_tips", True)
        pass

    def onPageRequest(self, event):
        page = event.context.page
        user = event.context.user
        request = event.context.request
        database = event.context.database
        send_event = event.context.server.send_event

        if event.page_matches("post/list"):
            if False and "search" in request.POST:
                search = request.POST["search"]
                page.mode = "redirect"
                if search:
                    page.redirect = make_link("post/list/1")
                else:
                    page.redirect = make_link("post/list/" + search + "/1")
                return

            search_terms = event.get_search_terms()
            page_number = event.get_page_number()
            page_size = event.get_page_size()
            count_search_terms = len(search_terms)

            try:
                total_pages = Image.count_pages(search_terms)
                images = Image.find_images((page_number-1)*page_size, page_size, search_terms)
            except SearchTermParseException:
                total_pages = 0
                images = []

            count_images = len(images)

            if count_search_terms == 0 and count_images == 0 and page_number == 1:
                self.theme.display_intro(page)

            elif count_search_terms > 0 and count_images == 1 and page_number == 1:
                page.mode = "redirect"
                page.redirect = make_link("post/view/" + images[0].id)

            else:
                plbe = PostListBuildingEvent(event.context, search_terms)
                send_event(plbe)

                self.theme.set_page(page, page_number, total_pages, search_terms)
                self.theme.display_page(page, images)

                if plbe.parts:
                    self.theme.display_admin_block(page, plbe.parts)

    def onSetupBuilding(self, event):
        sb = SetupBlock("Index Options", position=20)

        sb.add_label("Show ")
        sb.add_int_option("index_images")
        sb.add_label(" images on the post list")

        event.panel.add_block(sb)

    def onSearchTermParse(self, event):
        # TODO
        pass
