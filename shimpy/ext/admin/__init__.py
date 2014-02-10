from shimpy.core import Event, Extension, Themelet, PageRequestEvent
from shimpy.core.context import context
from shimpy.core.utils import make_link

import structlog

log = structlog.get_logger()


class AdminBuildingEvent(Event):
    pass


class AdminActionEvent(Event):
    def __init__(self, action):
        self.action = action
        self.redirect = False


class Admin(Extension):
    """
    Name: Admin Controls
    Author: Shish <webmaster@shishnet.org>
    Link: http://code.shishnet.org/shimmie2/
    License: GPLv2
    Description: Various things to make admins' lives easier
    Documentation:
        Various moderate-level tools for admins; for advanced, obscure, and
        possibly dangerous tools see the shimmie2-utils script set
        <p>Lowercase all tags:
        <br>Set all tags to lowercase for consistency
        <p>Recount tag use:
        <br>If the counts of images per tag get messed up somehow, this will
        reset them, and remove any unused tags
        <p>Database dump:
        <br>Download the contents of the database in plain text format, useful
        for backups.
        <p>Image dump:
        <br>Download all the images as a .zip file
    """
    def onPageRequest(self, event, user, send_event):
        if event.page_matches("admin"):
            if not user.can("manage_admintools"):
                self.theme.display_permission_denied()
            else:
                if event.count_args() == 0:
                    context.server.send_event(AdminBuildingEvent())
                else:
                    action = event.get_arg(0)
                    aae = AdminActionEvent(action)

                    if user.check_auth_token():
                        log.info("Running admin util", action=action)
                        send_event(aae)

                    if aae.redirect:
                        context.page.mode = "redirect"
                        context.page.redirect = make_link("admin")

    def onCommand(self, event):
        if event.cmd == "help":
            print "  get-page [query string]"
            print "    eg 'get-page post/list'"

        if event.cmd == "get-page":
            context.server.send_event(PageRequestEvent(event.args[0]))
            print context.page.render()

    def onAdminBuilding(self, event):
        self.theme.display_page()
        self.theme.display_form()

    def onUserBlockBuilding(self, event, user):
        if user.can("manage_admintools"):
            event.add_link("Board Admin", make_link("admin"))

    def onAdminAction(self, event):
        if hasattr(self, event.action):
            event.redirect = getattr(self, event.action)()

    def onPostListBuilding(self, event, user):
        if user.can("manage_admintools") and event.search_terms:
            event.add_control(self.theme.dbq_html(" ".join(event.search_terms)))

    def delete_by_query(self):
        query = context.request.form['query']
        reason = context.request.form['reason']

        assert query

        log.warning("Mass deleting", query=query)
        count = 0
        # TODO
        log.debug("Deleted images", count=count)

        context.page.mode = "redirect"
        context.page.redirect = make_link("post/link")
        return False

    def set_tag_case(self):
        context.database.execute(
            "UPDATE tags SET tag=:tag WHERE SCORE_STRNORM(tag) = SCORE_STRNORM(:tag)",
            {"tag": context.request.form['tag']}
        )
        log.info("Fixed the case of a tag", tag=context.request.form['tag'])
        return True

    def lowercase_all_tags(self):
        context.database.execute(
            "UPDATE tags SET tag=LOWER(tag)",
        )
        log.info("Set all tags to lowercase")
        return True

    def recount_tag_use(self):
        context.database.Execute("""
            UPDATE tags
            SET count = COALESCE(
                (SELECT COUNT(image_id) FROM image_tags WHERE tag_id=tags.id GROUP BY tag_id),
                0
            )
        """)
        context.database.execute("DELETE FROM tags WHERE count=0")
        log.warning("Re-counted tags")
        return True

    def database_dump(self):
        # TODO
        pass

    def download_all_images(self):
        # TODO
        pass

    def reset_image_ids(self):
        # TODO
        pass
