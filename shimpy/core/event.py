
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

class PageRequestEvent(Event):
    """
    A PageRequestEvent happens when a user (browser, robot, whatever)
    requests a page via HTTP(S)

    >>> from mock import Mock
    >>> ctx = Mock(request=Mock(path="/foo/bar/1"))
    >>> pre = PageRequestEvent(ctx)

    Path elements are matched from the front

    >>> pre.page_matches("foo")
    True
    >>> pre.page_matches("foo/baz")
    False
    >>> pre.page_matches("foo/bar")
    True

    Any path elements that aren't part of the match are considered arguments
    >>> pre.get_arg(0)
    '1'

    """
    def __init__(self, context):
        Event.__init__(self, context)
        self.args = []

    def page_matches(self, page):
        req_path = self.context.request.path.lstrip("/")
        if req_path.startswith(page):
            arg_str = req_path[len(page):].lstrip("/")
            self.args = arg_str.split("/")
            return True
        return False

    def get_arg(self, idx):
        return self.args[idx]
