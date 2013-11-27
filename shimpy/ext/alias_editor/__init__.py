from shimpy.core import Event, Extension, Themelet
from shimpy.core.context import context


class AddAliasEvent(Event):
    def __init__(self, oldtag, newtag):
        self.oldtag = oldtag
        self.newtag = newtag


class AddAliasException(Exception):
    pass


class AliasEditor(Extension):
    # add alias *after* mass tag editing, else the MTE will
    # search for the images and be redirected to the alias,
    # missing out the images tagged with the oldtag
    priority = 60

    def onPageRequest(self, event):
        user = context.user
        request = context.request
        send_event = context.server.send_event

        if event.page_matches("alias"):
            if event.get_arg(0) == "add":
                if user.can("manage_alias_list"):
                    if "oldtag" in request.form and "newtag" in request.form:
                        try:
                            aae = AddAliasEvent(request.form["oldtag"], request.form["newtag"])
                            send_event(aae)
                            page.mode = "redirect"
                            page.redirect = make_link("alias/list")
                        except AddAliasEvent as e:
                            self.theme.display_exception(e)

            elif event.get_arg(0) == "remove":
                if user.can("manage_alias_list"):
                    if "oldtag" in request.form:
                        database.query(Alias).filter(Alias.oldtag == request.form["oldtag"]).delete()
                        log.info("Deleted alias for %s", request.form["oldtag"])
                        page.mode = "redirect"
                        page.redirect = make_link("alias/list")

            elif event.get_arg(0) == "list":
                page_number = int(event.get_arg(1))
                aliases_per_page = int(config.get("alias_items_per_page", 30))

                aliases = database.query(Alias)
                pages = aliases.count() / aliases_per_page

                self.theme.display_aliases(aliases, page_number, total_pages)

            elif event.get_arg(0) == "export":
                page.mode = "data"
                page.content_type = "text/plain"
                page.data = self.get_alias_csv()

            elif event.get_arg(0) == "import":
                if user.can("manage_alias_list"):
                    if request.files:
                        # TODO get data
                        self.add_alias_csv(data)
                        log.info("Imported aliases from file")
                        page.mode = "redirect"
                        page.redirect = make_link("alias/list")

    def onAddAlias(self, event):
        database = context.database

        if database.query(Alias).filter(Alias.oldtag == event.newtag).first():
            raise AddAliasException("%s itself is an alias" % event.newtag)

        database.add(Alias(event.oldtag, event.newtag))

    def onUserBlockBuilding(self, event):
        user = context.user
        if user.can("manage_alias_list"):
            event.add_link("Alias Editor", make_link("alias/list"))

    def get_alias_csv(self):
        # TODO: csvlib?
        database = context.database
        data = []
        for alias in database.query(Alias):
            data.append([alias.oldtag, alias.newtag])
        return ",".join(data)

    def add_alias_csv(self, data):
        for row in data.split("\n"):
            parts = row.strip().split(",")
            database.add(Alias(parts[0], parts[1]))
