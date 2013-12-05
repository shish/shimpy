
import re
from flexihash import Flexihash

_balance_pattern = re.compile("(.*){(.*)}(.*)")
_balancers = {}


def balance(tmpl):
    """
    >>> balance("http://mirror-{001,002,003}.foo.com/filename01.png")
    'http://mirror-002.foo.com/filename01.png'
    >>> balance("http://mirror-{001,002,003}.foo.com/filename02.png")
    'http://mirror-001.foo.com/filename02.png'
    >>> balance("http://mirror-{001,002,003}.foo.com/filename03.png")
    'http://mirror-002.foo.com/filename03.png'
    >>> balance("http://mirror-{001,002,003}.foo.com/filename04.png")
    'http://mirror-002.foo.com/filename04.png'
    """
    matches = _balance_pattern.match(tmpl)
    if matches:
        pre = matches.group(1)
        opts = matches.group(2)
        post = matches.group(3)

        if opts not in _balancers:
            _balancers[opts] = Flexihash()
            opt_list = opts.split(",")
            for opt in opt_list:
                if "=" in opt:
                    val, weight = opt.split("=")
                else:
                    val, weight = opt, 1
                _balancers[opts].addTarget(val, int(weight))

        choice = _balancers[opts].lookup((pre + post).encode("ascii", "replace"))
        return pre + choice + post
    return tmpl
