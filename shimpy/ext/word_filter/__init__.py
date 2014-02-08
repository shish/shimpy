from shimpy.core import Event, Extension, Themelet
from shimpy.core.context import context

import re


class WordFilter(Extension):
    """
    Name: Word Filter
    Author: Shish <webmaster@shishnet.org>
    Link: http://code.shishnet.org/shimmie2/
    License: GPLv2
    Description: Simple search and replace
    """
    priority = 40  # before emoticon filter

    def onTextFormatting(self, event):
        event.formatted = self._filter(event.formatted)
        event.stripped = self._filter(event.stripped)

    def onSetupBuilding(self, event):
        sb = SetupBlock("Word Filter")
        sb.add_longtext_option("word_filter")
        sb.add_label("<br>(each line should be search term and replace term, separated by a comma)")
        event.panel.add_block(sb)

    def _filter(self, text):
        """
        >>> context.config = {
        ...     "word_filter": "cake,frog"
        ... }
        >>> wf = WordFilter()
        >>> wf._filter("foo cake bar")
        'foo frog bar'
        >>> wf._filter("foo shortcake bar")
        'foo shortcake bar'
        """
        map_ = self._get_map()
        for search, replace in map_.items():
            search = search.strip()
            replace = replace.strip()
            search = r"\b" + search + r"\b"
            text = re.sub(search, replace, text, re.IGNORECASE)
        return text

    def _get_map(self):
        """
        >>> context.config = {
        ...     "word_filter": "cake,frog\\nfoo,bar\\n1,2,3\\n1\\n\\n"
        ... }
        >>> wf = WordFilter()
        >>> wf._get_map()
        {'cake': 'frog', 'foo': 'bar'}
        """
        raw = context.config.get("word_filter", "")
        map_ = {}
        for line in raw.split("\n"):
            parts = line.split(",")
            if len(parts) == 2:
                map_[parts[0]] = parts[1]
        return map_


