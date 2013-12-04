from shimpy.core import Extension, Block
from shimpy.core.database import Base
from shimpy.core.context import context

from fnmatch import fnmatch
from sqlalchemy import Column, Integer, String, Unicode, UnicodeText


class DataBlock(Base):
    __tablename__ = "blocks"
    id = Column(Integer, primary_key=True)
    pages = Column(String(128), nullable=False)
    title = Column(Unicode(128), nullable=False)
    area = Column(String(16), nullable=False)
    priority = Column(Integer, nullable=False)
    content = Column(UnicodeText, nullable=False)


class Blocks(Extension):
    """
    Name: Generic Blocks
    Author: Shish <webmaster@shishnet.org>
    Link: http://code.shishnet.org/shimmie2/
    License: GPLv2
    Description: Add HTML to some space (News, Ads, etc)
    """

    def onUserBlockBuilding(self, event):
        if context.user.can("manage_blocks"):
            event.add_link("Blocks Editor", make_link("blocks/list"))

    def onPageRequest(self, event):
        config = context.config
        database = context.database
        page = context.page
        user = context.user
        cache = context.cache

        blocks = cache.get("blocks")
        if not blocks:
            blocks = database.query(DataBlock).all()
            cache.set("blocks", blocks, 600)

        for block in blocks:
            if fnmatch(block.pages, "/".join(event.args)):
                page.add_block(Block(block.title, block.content, block.area, block.priority))

        if event.page_matches("blocks") and user.can("manage_blocks"):
            if event.get_arg(0) == "add":
                if user.check_auth_token():
                    database.add(DataBlock(
                        pages=POST["pages"],
                        title=POST["title"],
                        area=POST["area"],
                        priority=POST["priority"],
                        content=POST["content"],
                    ))
                    log.info("blocks", "Added Block #" + (database.get_last_insert_id('blocks_id_seq')) + " (" + _POST['title'] + ")")
                    cache.delete("blocks")
                    page.mode = "redirect"
                    page.redirect = make_link("blocks/list")

            elif event.get_arg(0) == "update":
                if user.check_auth_token():
                    if _POST['delete']:
                        database.query(DataBlock).get(POST["id"]).delete()
                        log.info("blocks", "Deleted Block #" + _POST['id'])
                    else:
                        bl = database.query(DataBlock).get(POST["id"])
                        bl.pages = POST["pages"]
                        bl.title = POST["title"]
                        bl.area = POST["area"]
                        bl.priority = POST["priority"]
                        bl.content = POST["content"]
                        log.info("blocks", "Updated Block #" + _POST['id'] + " (" + _POST['title'] + ")")
                    cache.delete("blocks")
                    page.mode = "redirect"
                    page.redirect = make_link("blocks/list")

            elif event.get_arg(0) == "list":
                self.theme.display_blocks(database.query(DataBlock).order_by("area", "priority"))
