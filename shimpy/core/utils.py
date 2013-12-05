from shimpy.core.context import context

import os


def make_dirs_for(filename):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))


def make_link(page=None, query=None):
    if not page:
        page = "post/list"  # TODO: config.get("main_page")
    link = "/" + page
    if query:
        page = page + "?" + query
    return link


def warehouse_path(base, name, create=True):
    splits = int(context.config.get("wh_splits", 1))
    ab = name[0:2]
    cd = name[2:4]

    if splits == 1:
        path = os.path.join(base, ab, cd, name)
    if splits == 2:
        path = os.path.join(base, ab, name)

    if create:
        make_dirs_for(path)

    return path


def data_path(name):
    path = os.path.join("data", name)
    make_dirs_for(path)
    return path


def get_thumbnail_size(orig_width, orig_height):
    if not orig_width:
        orig_width = 192
    if not orig_height:
        orig_height = 192

    if orig_width > orig_height * 5:
        orig_width = orig_height * 5
    if orig_height > orig_width * 5:
        orig_height = orig_width * 5

    max_width = context.config.get("thumb_width")
    max_height = context.config.get("thumb_height")

    xscale = max_height / orig_height
    yscale = max_width / orig_width
    scale = xscale if xscale < yscale else yscale

    if scale > 1 and context.config.get("thumb_upscale"):
        scale = 1

    return (orig_width * scale, orig_height * scale)

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
