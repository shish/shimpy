from shimpy.core import Extension, Themelet, Event
from shimpy.core.models import Image, Tag
from shimpy.core.utils import SparseList, make_link
from shimpy.core.context import context

from sqlalchemy import not_, func

import logging
import re
from webhelpers.html import literal
from .theme import IndexTheme

log = logging.getLogger(__name__)


class SearchTermParseEvent(Event):
    def __init__(self, results, term, negative):
        self.results = results
        self.term = term
        self.negative = negative
        self.filter_added = False

    def add_filter(self, f):
        self.filter_added = True
        if self.negative:
            f = not_(f)
        self.results = self.results.filter(f)


class SearchTermParseException(Exception):
    pass


class PostListBuildingEvent(Event):
    def __init__(self, search_terms):
        self.search_terms = search_terms
        self.parts = SparseList()

    def add_control(self, html, position=50):
        self.parts.insert(position, html)


class Index(Extension):
    priority = 80  # STPE fallback needs to be last of the STPE handlers

    def __init__(self):
        self.theme = IndexTheme()
        #self.theme = Template(filename='shimpy/ext/index/theme.mako')

    def onInitExt(self, event):
        # context.config.set_default_int("index_images", 24)
        # context.config.set_default_bool("index_tips", True)
        pass

    def onPageRequest(self, event):
        page = context.page
        user = context.user
        request = context.request
        database = context.database
        send_event = context.server.send_event

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
                plbe = PostListBuildingEvent(search_terms)
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
        # TODO: search by tag count
        # TODO: search by ratio
        # TODO: search by filesize
        # TODO: search by id
        # TODO: search by hash / md5
        # TODO: search by filetype / ext
        # TODO: search by file name
        # TODO: search by source
        # TODO: search by posted
        # TODO: search by size

        # TODO: move to user ext
        m = re.match("^user_id=(\d+)$", event.term)
        if m:
            event.add_filter(Image.user_id == m.group(1))

        # TODO: move to numeric score ext
        m = re.match("^score([<>=]+)(\d+)$", event.term)
        if m:
            event.add_filter(Image.score.op(m.group(1))(m.group(2)))

        if not event.filter_added:
            # re.match("^[a-zA-Z0-9\'\_\-\.\(\)]+$", event.term):
            tag = Tag.get(event.term)
            if tag:
                log.info("Adding filter for plain tag: %s (%s)", event.term, tag.name)
                event.add_filter(Image.tags.contains(tag))
            else:
                if not event.negative:
                    # if the tag is negative, it doesn't
                    # matter that we couldn't find it
                    log.info("Tag %s not found", event.term)
                    event.add_filter(False)
