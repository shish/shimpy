from shimpy.core.event import Event
from shimpy.core.extension import Extension
from shimpy.core.database import Image


class DisplayingImageEvent(Event):
    def __init__(self, context, image):
        Event.__init__(self, context)
        self.image = image


class ImageInfoBoxBuildingEvent(Event):
    def __init__(self, context, image, user):
        Event.__init__(self, context)
        self.image = image
        self.user = context.user
        self.parts = {}

    def add_part(self, html, position):
        while self.parts.get(position):
            position += 1
        self.parts[position] = html


class ImageInfoSetEvent(Event):
    def __init__(self, context, image):
        Event.__init__(self, context)
        self.image = image


class ImageAdminBlockBuildingEvent(Event):
    def __init__(self, context, image, user):
        Event.__init__(self, context)
        self.image = image
        self.user = context.user
        self.parts = {}

    def add_part(self, html, position):
        while self.parts.get(position):
            position += 1
        self.parts[position] = html


class ViewImageTheme():
    def display_page(self, page, image, parts):
        page.header = "Image Found: %s" % image.hash
        page.add_block(Block(page.header, "image goes here"))

    def display_admin_block(self, page, parts):
        page.add_block(Block("Image Controls", "<br>".join(parts)))

    def display_error(self, page, status, header, body):
        page.status = status
        page.header = header
        page.add_block(Block(header, body))

class ViewImage(Extension):
    def __init__(self):
        self.theme = ViewImageTheme()

    def onPageRequest(self, event):
        page = event.context.page
        user = event.context.user
        database = event.context.database
        send_event = event.context.server.send_event

        if event.page_matches("post/view"):
            image_id = int(event.get_arg(0))

            image = database.query(Image).get(image_id)
            if image:
                send_event(DisplayingImageEvent(event.context, image))
            else:
                self.theme.display_error(page, 404, "Image not found", "No image in the database has the ID #%d" % image_id)

    def onDisplayingImage(self, event):
        user = event.context.user
        image = event.image

        iibbe = ImageInfoBoxBuildingEvent(event.context, image)
        send_event(iibbe)
        self.theme.display_page(event.context.page, event.image, iibbe.parts)

        iabbe = ImageAdminBlockBuildingEvent(event.context, image)
        send_event(iabbe)
        self.theme.display_admin_block(event.context.page, iabbe.parts)
