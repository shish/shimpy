from shimpy.core.extension import Extension
from shimpy.core.models import User


class Hello(Extension):
    def onPageRequest(self, event):
        users = context.database.query(User).all()
        if users:
            context.page.data = "Hello %s!" % (", ".join([u.username for u in users]))
        else:
            context.page.data = "Hello World!"
