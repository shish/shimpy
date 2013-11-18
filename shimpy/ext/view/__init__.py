from shimpy.core import Block, Event, Extension, Themelet
from shimpy.core.models import Image
from webhelpers.html import literal


class DisplayingImageEvent(Event):
    def __init__(self, context, image):
        Event.__init__(self, context)
        self.image = image


class ImageInfoBoxBuildingEvent(Event):
    def __init__(self, context, image):
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
    def __init__(self, context, image):
        Event.__init__(self, context)
        self.image = image
        self.user = context.user
        self.parts = {}

    def add_part(self, html, position):
        while self.parts.get(position):
            position += 1
        self.parts[position] = html


class ViewImageTheme(Themelet):
    def display_page(self, page, image, parts):
        page.heading = " ".join([t.name for t in image.tags])
        page.title = "Image %d: %s" % (image.id, page.heading)
        page.add_html_header(literal("<meta name=\"keywords\" content=\"%s\">") % image.tags_plain_text.replace(" ", ", "))
        page.add_html_header(literal("<meta property=\"og:title\" content=\"%s\">") % image.title)
        page.add_html_header(literal("<meta property=\"og:type\" content=\"article\">"))
        page.add_html_header(literal("<meta property=\"og:image\" content=\"%s\">") % image.thumb_url)
        page.add_html_header(literal("<meta property=\"og:url\" content=\"%s\">") % image.page_url)
        # TODO: navigation
        # TODO: image info
        page.add_block(Block("Image Found: %s" % image.fingerprint, "image goes here"))

    def display_admin_block(self, page, parts):
        page.add_block(Block("Image Controls", "<br>".join(parts), "left", 50))


class ViewImage(Extension):
    def __init__(self):
        self.theme = ViewImageTheme()

    def onPageRequest(self, event):
        page = event.context.page
        user = event.context.user
        database = event.context.database
        send_event = event.context.server.send_event

        if event.page_matches("post/prev") or event.page_matches("post/next"):
            # TODO
            pass

        if event.page_matches("post/view"):
            image_id = int(event.get_arg(0))

            image = database.query(Image).get(image_id)
            if image:
                send_event(DisplayingImageEvent(event.context, image))
            else:
                self.theme.display_error(page, 404, "Image not found", "No image in the database has the ID #%d" % image_id)

        if event.page_matches("post/set"):
            image_id = int(event.context.request.POST["image_id"])

            send_event(ImageInfoSetEvent(event.context, image))

            page.mode = "redirect"
            page.redirect = make_link("post/view/%d" % image_id, event.context.request.POST["query"])

    def onDisplayingImage(self, event):
        user = event.context.user
        image = event.image
        send_event = event.context.server.send_event

        iibbe = ImageInfoBoxBuildingEvent(event.context, image)
        send_event(iibbe)
        self.theme.display_page(event.context.page, event.image, iibbe.parts)

        iabbe = ImageAdminBlockBuildingEvent(event.context, image)
        send_event(iabbe)
        self.theme.display_admin_block(event.context.page, iabbe.parts)
