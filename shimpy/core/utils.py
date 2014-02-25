from shimpy.core.context import context
from shimpy.core.event import TextFormattingEvent

import re
import os
from urlparse import urljoin
import structlog

log = structlog.get_logger()


def flash_message(msg):
    log.info("Flashing message", message=msg)
    pass


def autodate(date):
    return str(date)[:16]


def format_text(text):
    tfe = TextFormattingEvent(text)
    context.server.send_event(tfe)
    return tfe.formatted


def captcha_check():
    return True


def make_dirs_for(path):
    """
    >>> make_dirs_for("/tmp/foodir/foo")
    >>> os.path.exists("/tmp/foodir")
    True
    >>> os.rmdir("/tmp/foodir")
    """
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))


def make_link(page=None, query=None):
    """
    >>> make_link()
    '/post/list'
    >>> make_link("foo/bar")
    '/foo/bar'
    >>> make_link("foo/bar", "cake=tasty")
    '/foo/bar?cake=tasty'
    """
    if not page:
        page = "post/list"  # TODO: config.get("main_page")
    link = "/" + page
    if query:
        link = link + "?" + query
    return link


def make_http(link):
    """
    >>> from mock import Mock
    >>> context.request = Mock(url="http://www.foo.com")
    >>> make_http("/foo/bar")
    'http://www.foo.com/foo/bar'
    >>> make_http("http://cake.com/foo/bar")
    'http://cake.com/foo/bar'
    """
    #log.debug(context.request.url)
    assert(isinstance(context.request.url, basestring))
    assert(isinstance(link, basestring))
    return urljoin(context.request.url, link)


def warehouse_path(base, name, create=True):
    """
    >>> context.config = {"wh_splits": 2}
    >>> warehouse_path("images", "abcd1234", create=False)
    'images/ab/cd/abcd1234'

    >>> context.config = {"wh_splits": 1}
    >>> warehouse_path("images", "abcd1234", create=False)
    'images/ab/abcd1234'
    """
    splits = int(context.config.get("wh_splits", 1))
    ab = name[0:2]
    cd = name[2:4]

    if splits == 2:
        path = os.path.join(base, ab, cd, name)
    if splits == 1:
        path = os.path.join(base, ab, name)

    if create:
        make_dirs_for(path)

    return path


def data_path(name, create=True):
    """
    >>> data_path("cake", create=False)
    'data/cake'
    """
    path = os.path.join("data", name)
    if create:
        make_dirs_for(name)
    return path


def get_thumbnail_size(orig_width, orig_height):
    """
    >>> context.config = {"thumb_width": 100, "thumb_height": 100, "thumb_upscale": False}
    >>> get_thumbnail_size(100, 100)
    (100, 100)
    >>> get_thumbnail_size(200, 100)
    (100, 50)
    >>> get_thumbnail_size(100, 50)
    (100, 50)
    >>> get_thumbnail_size(50, 25)
    (50, 25)

    >>> context.config = {"thumb_width": 100, "thumb_height": 100, "thumb_upscale": True}
    >>> get_thumbnail_size(50, 25)
    (100, 50)
    """
    if not orig_width:
        orig_width = 192
    if not orig_height:
        orig_height = 192

    if orig_width > orig_height * 5:
        orig_width = orig_height * 5
    if orig_height > orig_width * 5:
        orig_height = orig_width * 5

    max_width = float(context.config.get("thumb_width"))
    max_height = float(context.config.get("thumb_height"))

    xscale = max_height / orig_height
    yscale = max_width / orig_width
    scale = xscale if xscale < yscale else yscale

    if scale > 1 and not context.config.get("thumb_upscale"):
        scale = 1

    return (int(orig_width * scale), int(orig_height * scale))


def sAND(a, b):
    from array import array
    aa = array("B", a)
    ab = array("B", b)
    for n in range(len(aa)):
        aa[n] &= ab[n]
    return aa.tostring()


def get_session_ip(addr):
    if not addr:
        return "0.0.0.0"
    from socket import AF_INET, inet_pton, inet_ntop
    mask = context.config.get("session_hash_mask", "255.255.0.0")
    addr = inet_ntop(AF_INET, sAND(inet_pton(AF_INET, addr), inet_pton(AF_INET, mask)))
    return addr


class SparseList(object):
    """
    A vaguely listy thing which allows things to be inserted
    at numbered positions (multiple items can be inserted at
    the same index, and not every index position needs taking)

    >>> s = SparseList()
    >>> s[4] = "end"
    >>> s[1] = "cake"
    >>> s[2] = "fish"
    >>> s[1] = "pie"
    >>> list(s)
    ['cake', 'pie', 'fish', 'end']
    """
    def __init__(self):
        self.values = {}

    def __setitem__(self, pos, val):
        pos = float(pos)
        while pos in self.values:
            pos = pos + (1.0/128.0)
        self.values[pos] = val

    def __getitem__(self, pos):
        return list(self)[pos]

    def __iter__(self):
        keys = sorted(self.values.keys())
        for key in keys:
            yield self.values[key]


class ReCheck(object):
    def __init__(self):
        self.result = None

    def search(self, pattern, text):
        """
        >>> r = ReCheck()
        >>> m = r.search("f(o+)b", "foobar")
        >>> m == r.result
        True
        >>> r.group(1)
        'oo'
        """
        self.result = re.search(pattern, text)
        return self.result

    def match(self, pattern, text):
        """
        >>> r = ReCheck()
        >>> m = r.match("f(o+)b", "foobar")
        >>> m == r.result
        True
        >>> r.groups()
        ('oo',)
        """
        self.result = re.match(pattern, text)
        return self.result

    def group(self, n):
        return self.result.group(n)

    def groups(self):
        return self.result.groups()
