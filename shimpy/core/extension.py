from shimpy.core.context import context
from shimpy.core.utils import warehouse_path
from shimpy.core.models import Image


class Extension(object):
    priority = 50

    def __init__(self):
        self.theme = None

    def __cmp__(self, other):
        return cmp(self.priority, other.priority)


class FormatterExtension(Extension):
    def onTextFormatting(self, event):
        event.formatted = self.format(event.formatted)
        event.stripped = self.format(event.stripped)

    def format(self, text):
        raise NotImplemented("Base FormatterExtension does nothing, needs subclasses")

    def strip(self, text):
        raise NotImplemented("Base FormatterExtension does nothing, needs subclasses")


class DataHandlerExtension(Extension):
    def onDataUpload(self, event, database, send_event):
        if self.is_supported_ext(event.type) and self.check_contents(event.tmpname):
            if not move_upload_to_archive(event):
                return

            send_event(ThumbnailGenerationEvent(event.hash, event.type))

            if "replace" in event.metadata:
                image_id = int(event.metadata["replace"])
                existing = database.query(Image).get(image_id)

                if not existing:
                    raise UploadException("Image to replace does not exist")

                if existing.hash == event.metadata["hash"]:
                    raise UploadException("The uploaded image is the same as the one to replace.")

                event.metadata["tags"] = existing.get_tag_list()

                image = self.create_image_from_data(warehouse_path("images", event.metadata["hash"]), event.metadata)

                if not image:
                    raise UploadException("Data handler failed to create image object from data")

                ire = ImageReplaceEvent(image_id, image)
                send_event(ire)
                event.image_id = image_id

            else:
                image = self.create_image_from_data(warehouse_path("images", event.metadata["hash"]), event.metadata)
                if not image:
                    raise UploadException("Data handler failed to create image object from data")

                iae = ImageAdditionEvent(image)
                send_event(iae)
                event.image_id = iae.image.id

                # TODO: rating stuff
                # TODO: locked stuff

    def onThumbnailGeneration(self, event):
        if self.is_supported_ext(event.type):
            # TODO: create_thumb_force
            self.create_thumb(event.hash)

    def onDisplayingImage(self, event):
        if self.is_supported_ext(event.image.ext):
            self.theme.display_image(context.page, event.image)

    def is_supported_ext(self, ext):
        raise NotImplemented()

    def check_contents(self, filename):
        raise NotImplemented()

    def create_image_from_data(self, filename, metadata):
        raise NotImplemented()

    def create_thumb(self, thumb):
        raise NotImplemented()
