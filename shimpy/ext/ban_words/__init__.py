from shimpy.core import Extension, Event
from shimpy.core.context import context

from textwrap import dedent
import re


class BanWords(Extension):
    """
    Name: Comment Word Ban
    Author: Shish <webmaster@shishnet.org>
    Link: http://code.shishnet.org/shimmie2/
    License: GPLv2
    Description: For stopping spam and other comment abuse
    Documentation:
        Allows an administrator to ban certain words
        from comments. This can be a very simple but effective way
        of stopping spam; just add "viagra", "porn", etc to the
        banned words list.
        <p>Regex bans are also supported, allowing more complicated
        bans like <code>/http:.*\.cn\//</code> to block links to
        chinese websites, or <code>/.*?http.*?http.*?http.*?http.*?/</code>
        to block comments with four (or more) links in.
        <p>Note that for non-regex matches, only whole words are
        matched, eg banning "sex" would block the comment "get free
        sex call this number", but allow "This is a photo of Bob
        from Essex"
    """
    priority = 30

    def onInitExt(self, event):
        """
        >>> from shimpy.core.event import InitExtEvent
        >>> context.config = {}

        >>> bw = BanWords()
        >>> bw.onInitExt(InitExtEvent())
        >>> "viagra" in context.config.get("banned_words")
        True
        """
        # TODO: dedent
        if "banned_words" not in context.config:
            context.config["banned_words"] = dedent("""
                viagra
                xanax
                """)

    def onCommentPosting(self, event):
        self.__test(event.comment, CommentPostingException("Comment contains banned terms"))

    def onSourceSet(self, event):
        self.__test(event.source, Exception("Source contains banned terms"))

    def onTagSet(self, event):
        # TODO: tags.join
        self.__test(" ".join(event.tags), Exception("Tags contain banned terms"))

    def onSetupBuilding(self, event):
        sb = SetupBlock()
        sb.add_label("One per line, lines that start with slashes are treated as regex<br/>")
        sb.add_longtext_option("banned_words")
        event.panel.add_block(sb)

    def __test(self, text, exc):
        """
        >>> context.config = {"banned_words": \"\"\"
        ... viagra
        ... /r[aeiou]gex/
        ... \"\"\"}
        >>> bw = BanWords()
        >>> t = bw._BanWords__test
        >>> t("ok text", Exception("ex"))
        >>> t("vIaGrA", Exception("ex"))
        Traceback (most recent call last):
            ...
        Exception: ex
        >>> t("regex", Exception("ex"))
        Traceback (most recent call last):
            ...
        Exception: ex
        >>> t("rogex", Exception("ex"))
        Traceback (most recent call last):
            ...
        Exception: ex
        >>> t("rygex", Exception("ex"))
        """
        banned_list = context.config.get("banned_words").lower().split("\n")
        text = text.lower()

        for banned_word in banned_list:
            banned_word = banned_word.strip()

            # blank line
            if not banned_word:
                pass

            # regex
            elif banned_word[0] == "/":
                banned_regex = banned_word[1:-1]
                if re.match(banned_regex, text):
                    raise exc

            # plain text
            else:
                if banned_word in text:
                    raise exc
