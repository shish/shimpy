from shimpy.core.extension import Extension
from shimpy.core.models import User
from shimpy.core.context import context


class Hello(Extension):
    def onPageRequest(self, event):
        if event.page_matches("hello"):
            users = context.database.query(User).all()
            if users:
                context.page.data = "Hello %s!" % (", ".join([u.username for u in users]))
            else:
                context.page.data = "Hello World!"
