from shimpy.core import Extension, __version__
from shimpy.core.utils import make_link, make_http, format_text
from shimpy.core.context import context
from shimpy.core.models import Image

from webhelpers.html import HTML
import webhelpers.feedgenerator as feedgenerator


class ShimpyRSSFeed(feedgenerator.Rss201rev2Feed):
    def rss_attributes(self):
        attrs = super(ShimpyRSSFeed, self).rss_attributes()
        attrs[u'xmlns:wfw'] = u'http://wellformedweb.org/CommentAPI/'
        attrs[u'xmlns:atom'] = u'http://www.w3.org/2005/Atom'
        return attrs

    def add_root_elements(self, handler):
        feedgenerator.Rss201rev2Feed.add_root_elements(self, handler)
        if self.feed["generator"] is not None:
            handler.addQuickElement(u"generator", self.feed['generator'])
        if self.feed["prev"] is not None:
            handler.addQuickElement('atom:link', attrs={"rel": "previous", "href": self.feed["prev"]})
        if self.feed["next"] is not None:
            handler.addQuickElement('atom:link', attrs={"rel": "next", "href": self.feed["next"]})

    def add_item_elements(self, handler, item):
        feedgenerator.Rss201rev2Feed.add_item_elements(self, handler, item)
        if item["commentRss"] is not None:
            handler.addQuickElement(u"wfw:commentRss", item['commentRss'])


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

    def onPageRequest(self, event, database):
        """
        >>> from shimpy.core.event import PageRequestEvent
        >>> from shimpy.core.page import Page
        >>> from mock import Mock, MagicMock
        >>> context.request = Mock(path="/rss/images/1", url="http://foo.com/rss/images/1")
        >>> context.config = {"title": "Site Title"}
        >>> context.page = Page()
        >>> context.database = MagicMock()
        >>> context._load_start = 0
        >>> context._event_count = 0
        >>> context.cache = Mock(hit_count=0, miss_count=0)
        >>> context.database.query().limit().offset().limit().all.return_value = []
        >>> ri = RSSImages()

        >>> pre = PageRequestEvent()
        >>> ri.onPageRequest(pre, context.database)
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
            context.get_debug_info()

        if event.page_matches("rss/image_comments"):
            image = database.query(Image).get(event.get_arg(0))

            context.page.mode = "data"
            context.page.content_type = "application/rss+xml"
            context.page.data = self.__do_comments(image)
            context.get_debug_info()

    def __do_rss(self, images, search_terms, page_number):
        """
        >>> from mock import Mock
        >>> import datetime
        >>> context.cache = Mock(get=Mock(return_value=None))
        >>> context.config = {"thumb_width": 192, "thumb_height": 192, "title": "Site Title"}
        >>> context.request = Mock(url="http://foo.com/rss/images")

        >>> data = RSSImages()._RSSImages__do_rss([
        ...     Image(id=4, user_id=1, fingerprint="cakecakckcacakec", posted=datetime.datetime.now(), user=Mock(username="bob"))
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
        href_prev = make_http(make_link("rss/images/%s%d" % (search, page_number - 1)))
        href_next = make_http(make_link("rss/images/%s%d" % (search, page_number + 1)))

        feed = ShimpyRSSFeed(
            title=context.config.get("title"),
            link=make_http("/"),
            description="The latest uploads to the image board",
            language=u"en",
            feed_copyright="(c) 2014 Shish",
            generator="Shimpy-%s" % __version__,
            prev=href_prev if page_number > 1 else None,
            next=href_next if images else None,
        )

        for image in images:
            link = make_http(make_link("post/view/%d" % image.id))
            content = ("""
                <p>%(thumb)s</p>
                <p>Uploaded by %(name)s</p>
            """) % {
                "thumb": self.theme.build_thumb_html(image),
                "name": image.user.username,
            }

            feed.add_item(
                author_name=image.user.username,
                author_link=make_http(make_link("user/%s" % image.user.username)),
                commentRss=make_http(make_link("rss/image_comments/%d" % image.id)),
                title="%d - %s" % (image.id, image.tags_plain_text),
                link=link,
                description=content,
                pubdate=image.posted,
                enclosure=feedgenerator.Enclosure(image.image_url, str(image.file_size), image.mime_type),
            )

            #ET.SubElement(item, "guid", {"isPermaLink": "true"}).text = link
            #ET.SubElement(item, "media:thumbnail", {"url": image.thumb_url})
            #ET.SubElement(item, "media:content", {"url": image.image_url})

        return feed.writeString("utf-8")

    def __do_comments(self, image):
        feed = feedgenerator.Rss201rev2Feed(
            title="Comments for image %d" % image.id,
            link=make_http("post/view/%d" % image.id),
            description="",
            language=u"en",
        )
        for c in image.comments:
            feed.add_item(
                author_name=c.user.username,
                author_link=make_http(make_link("user/%s" % c.user.username)),
                title="Comment by %s" % c.user.username,
                link="",
                description=format_text(c.body),
                pubdate=c.posted,
            )

        return feed.writeString("utf-8")
