
def make_link(page=None, query=None):
    if not page:
        page = "post/list"  # TODO: config.get("main_page")
    link = "/" + page
    if query:
        page = page + "?" + query
    return link


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

    def __iter__(self):
        keys = sorted(self.values.keys())
        for key in keys:
            yield self.values[key]
