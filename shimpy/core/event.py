
class Event(object):
    """
    A basic event class, just carries a Context around with it

    >>> from mock import Mock
    >>> ctx = Mock()
    >>> e = Event(ctx)
    >>> e.context == ctx
    True

    Devs are expected to subclass this to send events around
    """
    def __init__(self, context):
        self.context = context


class InitExtEvent(Event):
    """
    A wake-up call for extensions. Upon recieving an InitExtEvent an extension
    should check that it's database tables are there and install them if not,
    and set any defaults with Config::set_default_int() and such.
    """
    pass


class PageRequestEvent(Event):
    """
    A PageRequestEvent happens when a user (browser, robot, whatever)
    requests a page via HTTP(S)
    """
    def __init__(self, context):
        """
        >>> from mock import Mock
        >>> pre = PageRequestEvent(Mock(request=Mock(path="/"), config={"front_page": "post/list"}))

        If the path is blank, the configured front_page will be used

        >>> pre.page_matches("post/list")
        True
        """
        Event.__init__(self, context)
        self.path = self.context.request.path.lstrip("/")
        self.args = []

        if not self.path:
            self.path = context.config.get("front_page")

    def page_matches(self, page):
        """
        >>> from mock import Mock
        >>> pre = PageRequestEvent(Mock(request=Mock(path="/foo/bar/1")))

        Path elements are matched from the front

        >>> pre.page_matches("foo")
        True
        >>> pre.page_matches("foo/baz")
        False
        >>> pre.page_matches("foo/bar")
        True
        """
        req_path = self.path
        if req_path.startswith(page):
            arg_str = req_path[len(page):].lstrip("/")
            self.args = arg_str.split("/")
            return True
        return False

    def get_arg(self, idx):
        """
        >>> from mock import Mock
        >>> pre = PageRequestEvent(Mock(request=Mock(path="/foo/bar/1")))

        Any path elements that aren't part of the match are considered arguments

        >>> pre.page_matches("foo/bar")
        True
        >>> pre.get_arg(0)
        '1'
        """
        return self.args[idx]

    def count_args(self):
        """
        >>> from mock import Mock
        >>> pre = PageRequestEvent(Mock(request=Mock(path="/foo/bar/1")))

        Count the number of path parts that weren't matched

        >>> pre.page_matches("foo")
        True
        >>> pre.count_args()
        2
        """
        return len(self.args)

    # bits that are imageboard specific, but commonly used enough to warrant being common
    def get_search_terms(self):
        if self.count_args() == 2:
            return self.get_arg(0).split()
        return []

    def get_page_number(self):
        page_number = 1
        if self.count_args() == 1:
            page_number = int(self.get_arg(0))
        if self.count_args() == 2:
            page_number = int(self.get_arg(1))
        if page_number == 0:
            page_number = 1
        return page_number

    def get_page_size(self):
        return self.context.config.get("index_images")


class CommandEvent(Event):
    def __init__(self, args):
        self.cmd = "help"
        self.args = []

        # TODO: argparse
        # -u username
        # -q log level -= 10
        # -v log level += 10

        if args:
            self.cmd = args[0]
            self.args = args[1:]
        else:
            # TODO: print usage
            pass


class TextFormattingEvent(Event):
    def __init__(self, text):
        self.original = text
        self.formatted = text
        self.stripped = text
