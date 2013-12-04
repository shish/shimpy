from shimpy.core import Extension, __version__
from shimpy.core.utils import make_link
from shimpy.core.context import context
from shimpy.core.models import Image

import xml.etree.ElementTree as ET
from webhelpers.html import HTML


class RSSImages(Extension):
    """
    Name: RSS for Images
    Author: Shish <webmaster@shishnet.org>
    Link: http://code.shishnet.org/shimmie2/
    License: GPLv2
    Description: Self explanatory
    """
    def onPostListBuilding(self, event):
        """
        >>> from shimpy.ext.index import PostListBuildingEvent
        >>> from shimpy.core.page import Page
        >>> from mock import Mock
        >>> context.config = {"title": "Site Title"}
        >>> ri = RSSImages()

        >>> context.page = Page()
        >>> ri.onPostListBuilding(PostListBuildingEvent([]))
        >>> context.page.html_headers[0]
        literal(u'<link href="/rss/images/1" id="images" rel="alternate" title="Site Title - Images" type="application/rss+xml" />')

        >>> context.page = Page()
        >>> ri.onPostListBuilding(PostListBuildingEvent(["search", "terms"]))
        >>> context.page.html_headers[0]
        literal(u'<link href="/rss/images/search terms/1" id="images" rel="alternate" title="Site Title - Images with tags: search terms" type="application/rss+xml" />')
        """
        title = context.config.get("title")

        if event.search_terms:
            search = " ".join(event.search_terms)
            feed_title = "%s - Images with tags: %s" % (title, search)
            link = make_link("rss/images/%s/1" % search)
        else:
            feed_title = "%s - Images" % title
            link = make_link("rss/images/1")
        context.page.add_html_header(HTML.link(
            id="images", rel="alternate", type="application/rss+xml",
            title=feed_title, href=link
        ))

    def onPageRequest(self, event):
        """
        >>> from shimpy.core.event import PageRequestEvent
        >>> from shimpy.core.page import Page
        >>> from mock import Mock
        >>> context.request = Mock(path="/rss/images/1")
        >>> context.config = {"title": "Site Title"}
        >>> context.page = Page()
        >>> context.database = Mock()
        >>> context.database.query().limit().offset().limit().all.return_value = []
        >>> ri = RSSImages()

        >>> pre = PageRequestEvent()
        >>> ri.onPageRequest(pre)
        >>> context.page.mode
        'data'
        >>> context.page.content_type
        'application/rss+xml'
        """
        if event.page_matches("rss/images"):
            search_terms = event.get_search_terms()
            page_number = event.get_page_number()
            page_size = event.get_page_size()
            images = Image.find_images((page_number-1)*page_size, page_size, search_terms)

            context.page.mode = "data"
            context.page.content_type = "application/rss+xml"
            context.page.data = self.__do_rss(images, search_terms, page_number)

    def __do_rss(self, images, search_terms, page_number):
        """
        >>> data = RSSImages()._RSSImages__do_rss([
        ...     Image(id=4, user_id=1, fingerprint="cakecakckcacakec")
        ... ], [], 1)
        >>> '/rss/images/0' in data  # prev page link
        False
        >>> '/rss/images/2' in data  # next page link
        True
        >>> '<item>' in data  # an item
        True
        >>> 'cakecakckcacakec' in data
        True

        >>> data = RSSImages()._RSSImages__do_rss([], ['search', 'terms'], 2)
        >>> '/rss/images/search terms/1' in data  # prev page link
        True
        >>> '/rss/images/search terms/3' in data  # next page link
        False
        >>> '<item>' in data  # no items
        False
        """
        search = ""
        if search_terms:
            search = " ".join(search_terms) + "/"
        href_prev = make_link("rss/images/%s%d" % (search, page_number - 1))
        href_next = make_link("rss/images/%s%d" % (search, page_number + 1))

        root = ET.Element('rss', {
            'version': '2.0',
            'xmlns:media': "http://search.yahoo.com/mrss",
            'xmlns:atom': "http://www.w3.org/2005/Atom",
        })

        channel = ET.SubElement(root, 'channel')
        ET.SubElement(channel, 'title').text = "Title"
        ET.SubElement(channel, 'description').text = "The latest uploads to the image board"
        ET.SubElement(channel, 'link').text = make_link("post/list")
        ET.SubElement(channel, 'generator').text = "Shimpy-%s" % __version__

        if page_number > 1:
            ET.SubElement(channel, 'atom:link', {"rel": "previous", "href": href_prev})
        if images:
            ET.SubElement(channel, 'atom:link', {"rel": "next", "href": href_next})

        for image in images:
            link = make_link("post/view/%d" % image.id)
            posted = ""
            content = ""

            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = "%d - %s" % (image.id, image.tags_plain_text)
            ET.SubElement(item, "link").text = link
            ET.SubElement(item, "guid", {"isPermaLink": "true"}).text = link
            ET.SubElement(item, "pubDate").text = posted
            ET.SubElement(item, "description").text = content
            ET.SubElement(item, "media:thumbnail", {"url": image.thumb_url})
            ET.SubElement(item, "media:content", {"url": image.image_url})

        return ET.tostring(root)