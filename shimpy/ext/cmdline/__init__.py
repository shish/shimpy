from shimpy.core import Event, Extension, Themelet, PageRequestEvent
from shimpy.core.context import context
from shimpy.core.utils import make_link
from shimpy.core.models import Alias, Image, Tag
from mock import Mock


class CmdLine(Extension):
    def onCommand(self, event, page, database, config, send_event):
        if event.cmd == "help":
            print "CmdLine commands:"
            print "  get-page /foo/bar"
        if event.cmd == "shell":
            import pudb
            pudb.set_trace()
        if event.cmd == "get-page":
            context.request = Mock(
                path=event.args[0],
                url=event.args[0],
                args={},
            )
            send_event(PageRequestEvent())
            page.render()
            print page.data

