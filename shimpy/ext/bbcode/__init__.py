from shimpy.core.extension import FormatterExtension
from shimpy.core.utils import make_link
import bbcode


class BBCode(FormatterExtension):
    def __init__(self):
        FormatterExtension.__init__(self)
        self.parser = bbcode.Parser()

    # TODO
    def format(self, text):
        text = text.replace("site://", make_link("/"))
        return self.parser.format(text)

    def strip(self, text):
        return text
