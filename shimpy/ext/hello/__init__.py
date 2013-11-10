from shimpy.core.extension import Extension
from shimpy.core.database import User

class Hello(Extension):
    def onPageRequest(self, event):
        users = event.context.database.query(User).all()
        if users:
            event.context.page.data = "Hello %s!" % (", ".join([u.username for u in users]))
        else:
            event.context.page.data = "Hello World!"
