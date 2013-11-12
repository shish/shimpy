from webhelpers.html import literal


def get_debug_info():
    return ""


class Layout(object):
    def display_page(self, page, context):
        left_block_html = ""
        main_block_html = ""
        sub_block_html = ""

        header_html = literal("\n").join(page.html_headers)

        for block in page.blocks:
            if block.section == "left":
                left_block_html += block.__html__(True)
            if block.section == "main":
                main_block_html += block.__html__(False)
            if block.section == "sub":
                sub_block_html += block.__html__(False)

        debug = get_debug_info()

        contact_link = context.config.get("contact_link")
        if contact_link:
            contact = literal("<br><a href='mailto:%s'>Contact</a>") % contact_link
        else:
            contact = ""

        flash_html = ""

        wrapper = ""
        if len(page.heading) > 100:
            wrapper = ' style="height: 3em; overflow: auto;"'

        return literal("""
<!doctype html>
<!--[if lt IE 7]> <html class="no-js lt-ie9 lt-ie8 lt-ie7" lang="en"> <![endif]-->
<!--[if IE 7]>    <html class="no-js lt-ie9 lt-ie8" lang="en"> <![endif]-->
<!--[if IE 8]>    <html class="no-js lt-ie9" lang="en"> <![endif]-->
<!--[if gt IE 8]><!--> <html class="no-js" lang="en"> <!--<![endif]-->
    <head>
        <title>%(title)s</title>
%(header_html)s
    </head>

    <body>
        <header>
            <h1%(wrapper)s>%(heading)s</h1>
            %(sub_block_html)s
        </header>
        <nav>
            %(left_block_html)s
        </nav>
        <article>
            %(flash_html)s
            %(main_block_html)s
        </article>
        <footer>
            Images &copy; their respective owners,
            <a href="http://github.com/shish/shimpy/">Shimpy</a> &copy;
            <a href="http://www.shishnet.org/">Shish</a> &amp;
            <a href="https://github.com/shish/shimpy/contributors">The Team</a>
            2013.
            %(debug)s
            %(contact)s
        </footer>
    </body>
</html>
        """.strip()) % {
            "title": page.title,
            "heading": page.heading,
            "debug": debug,
            "contact": contact,
            "header_html": header_html,
            "flash_html": flash_html,
            "left_block_html": left_block_html,
            "main_block_html": main_block_html,
            "sub_block_html": sub_block_html,
            "wrapper": wrapper,
        }
