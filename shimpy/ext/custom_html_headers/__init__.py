from shimpy.core import Event, Extension, Themelet
from shimpy.core.context import context


class CustomHTMLHeaders(Extension):
    """
    Name: Custom HTML Headers
    Author: Drudex Software <support@drudexsoftware.com>
    Link: http://www.drudexsoftware.com
    License: GPLv2
    Description: Allows admins to modify & set custom &lt;head&gt; content
    Documentation:
        When you go to board config you can find a block named Custom HTML Headers.
        In that block you can simply place any thing you can place within &lt;head&gt;&lt;/head&gt;
        This can be useful if you want to add website tracking code or other javascript.
        NOTE: Only use if you know what you're doing.
        You can also add your website name as prefix or suffix to the title of each page on your website.
    """
    def onSetupBuilding(self, event):
        sb = SetupBlock("Custom HTML Headers")
        sb.add_longtext_option(
            "custom_html_headers",
            "HTML Code to place within &lt;head&gt;&lt;/head&gt; on all pages<br>"
        )
        sb.add_choice_option(
            "sitename_in_title",
            {
                "none": 1,
                "as prefix": 2,
                "as suffix": 3
            },
            "<br>Add website name in title"
        )
        event.panel.add_block(sb)

    def onInitExt(self, event):
        context.config.set_default_int("sitename_in_title", 0)

    def onPageRequest(self, event):
        self.handle_custom_html_headers()
        self.handle_modified_page_title()

    def handle_custom_html_headers(self):
        header = context.config.get_string('custom_html_headers', '')
        if header:
            context.page.add_html_header(header)

    def handle_modified_page_title(self):
        site_title = context.config.get_string("title")
        sitename_in_title = context.config.get_int("sitename_in_title")

        # if feature is enabled & sitename isn't already in title
        # (can occur on index & other pages)
        if sitename_in_title and site_title not in context.page.title:
            if sitename_in_title == 1:
                context.page.title = "%s - %s" % (site_title, context.page.title)  # as prefix
            elif sitename_in_title == 2:
                context.page.title = "%s - %s" % (context.page.title, site_title)  # as suffix

