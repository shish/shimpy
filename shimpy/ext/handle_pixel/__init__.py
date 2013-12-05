from shimpy.core.extension import DataHandlerExtension
from shimpy.core.models.post import Post
from shimpy.core.utils import warehouse_path, get_thumbnail_size
from shimpy.core.context import context
from shimpy.core import Themelet, Block

from PIL import Image
from webhelpers.html import HTML


class PixelFileHandlerTheme(Themelet):
    def display_image(self, page, post):
        img = HTML.img(
            alt="main image",
            class_="shm-main-image",
            id="main_image",
            src=post.image_url,
            data_width=post.width,
            data_height=post.height,
        )
        context.page.add_block(Block("Image", img, "main", 10))

class PixelFileHandler(DataHandlerExtension):
    def __init__(self):
        self.theme = PixelFileHandlerTheme()

    def is_supported_ext(self, ext):
        return ext in ["jpg", "jpeg", "gif", "png"]

    def create_image_from_data(filename, metadata):
        post = Post()

        post.width, post.height = Image.open(image_filename).size
        post.filesize = metadata["size"]
        post.fingerprint = metadata["hash"]
        post.filename = metadata["filename"]
        post.ext = metadata["extension"]
        post.tags = [Tag.get_or_create(t) for t in " ".split(metadata["tags"])]

        return post

    def check_contents(self, filename):
        try:
            Image.open(filename)
            return True
        except Exception:
            return False

    def create_thumb(self, fingerprint):
        in_name = warehouse_path("images", fingerprint)
        out_name = warehouse_path("thumbs", fingerprint)

        width, height = Image.open(image_filename).size

        Image.open(in_name)
        im.thumbnail(get_thumbnail_size(width, height), Image.ANTIALIAS)
        im.save(out_name, "JPEG")
        return True
