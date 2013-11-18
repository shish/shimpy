from shimpy.core import Extension, Themelet, Event
from shimpy.core.models import Image
from shimpy.core.utils import SparseList, make_link

import os
import logging
import re
from webhelpers.html import literal
from .theme import IndexTheme

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


class Index(Extension):
    def __init__(self):
        self.theme = IndexTheme()
        #self.theme = Template(filename='shimpy/ext/index/theme.mako')

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
            if "search" in request.args:
                search = request.args["search"]
                page.mode = "redirect"
                if search:
                    page.redirect = make_link("post/list/" + search + "/1")
                else:
                    page.redirect = make_link("post/list/1")
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
