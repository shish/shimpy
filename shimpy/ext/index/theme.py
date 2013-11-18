from shimpy.core import Block, NavBlock, Themelet
from shimpy.core.utils import make_link
from webhelpers.html import literal


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
        config = {"title": "Shimpy"}

        if not self.search_terms:
            query = None
            page_title = config.get("title")

        else:
            query = " ".join(self.search_terms)  # TODO: Tag.join()?
            page_title = query

            if images:
                page.subheading = "Page %d / %d" % (self.page_number, self.total_pages)

        page.title = page_title
        page.heading = page_title
        page.add_block(Block("Navigation", self.build_navigation(), "left", 0))

        if images:
            page.add_block(Block("Images", self.build_table(images, ("#search="+query) if query else None), "main", 10, "image-list"))
            self.display_paginator(page, "post/list/"+query if query else "post/list", None, self.page_number, self.total_pages)
        else:
            self.display_error(page, 404, "No Images Found", "No images were found to match the search criteria")

    def display_admin_block(self, page, parts):
        page.add_block(Block("List Controls", literal("<br>").join(parts), "left", 50))

    def build_navigation(self):
        query = " ".join(self.search_terms)
        prev_link = literal('<a href="%s">Prev</a>') % (make_link('post/list%s/%d') % (query, self.page_number - 1))
        next_link = literal('<a href="%s">Next</a>') % (make_link('post/list%s/%d') % (query, self.page_number + 1))

        tags = " ".join(self.search_terms)  # TODO: Tag.join()?
        prev = "Prev" if self.page_number <= 1 else prev_link
        index = literal('<a href="%s">Index</a>') % make_link()
        next = "Next" if self.page_number >= self.total_pages else next_link

        search_link = make_link("post/list")
        search = literal("""
            <p><form action="%s" method="GET">
                <input class="autocomplete_tags" name="search" type="text" placeholder="Search" value="%s" />
                <input type="hidden" name="q" value="/post/list" />
                <input type="submit" value="Find" style="display: none;" />
            </form>
        """) % (search_link, query)

        return prev + " | " + index + " | " + next + literal("<br>") + search

    def build_table(self, images, query):
        table = literal("""<div class="shm-image-list" data-query="%s">""") % query
        for image in images:
            table += self.build_thumb_html(image)
        table += literal( "</table>")
        return table
