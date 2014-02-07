from webhelpers.html import HTML, literal, tags
from shimpy.core.block import Block, NavBlock
from shimpy.core.themelet import Themelet
from shimpy.core.utils import make_link
from shimpy.core.context import context
from shimpy.core.models import User


class UserManagerTheme(Themelet):
    ###################################################################
    # Misc Full pages
    ###################################################################

    def display_login_page(self):
        page = context.page
        self.display_error(page, 400, "Error", "Login details missing")

    def display_signup_page(self):
        # TODO
        pass

    def display_signups_disabled(self):
        page = context.page
        page.title = "Signups Disabled"
        page.heading = "Signups Disabled"
        page.add_block(NavBlock())
        page.add_block(Block(
            "Signups Disabled",
            "The board admin has disabled the ability to create new accounts~"
        ))

    ###################################################################
    # User block (Login or User Links)
    ###################################################################

    def _user_block_location(self):
        if context.config.get("theme", "default") == "rule34":
            return "head"
        else:
            return "left"

    def display_user_links(self, user, parts):
        pass

    def display_user_block(self, user, parts):
        page = context.page

        html = "Logged in as %s" % user.username
        for part in parts:
            html = html + literal('<br><a href="%s">%s</a>') % (part["link"], part["name"])
        page.add_block(Block("User Links", html, self._user_block_location(), 90))

    def display_login_block(self):
        page = context.page
        table = HTML.table(
            HTML.tr(
                HTML.th("Username"),
                HTML.td(tags.text("username")),
            ),
            HTML.tr(
                HTML.th("Password"),
                HTML.td(tags.password("password")),
            ),
            HTML.tr(
                HTML.td(tags.submit(name="submit", value="Log In"), colspan=2)
            ),
            HTML.tr(
                HTML.td(HTML.small(HTML.a("Create Account", href=make_link("user_admin/create"))), colspan=2)
            ),
            # class_="form",
        )
        form = HTML.form(table, action=make_link("user_admin/login"), method="POST")
        page.add_block(Block("Login", form, self._user_block_location(), 90))

    ###################################################################
    # User List
    ###################################################################

    def display_user_list(self, users, user):
        page = context.page
        request = context.request

        page.title = "User List"
        page.heading = "User List"
        page.add_block(NavBlock(force_pager=True))

        headers = []
        tds = [
            HTML.th("ID", width="16"),
            HTML.th("Av.", width="16", title="Avatar"),
            HTML.th("Username"),
            HTML.th("Join Date"),
            HTML.th("Ps.", width="16", title="Post Count"),
            HTML.th("Cs.", width="16", title="Comment Count"),
        ]
        if user.can("view_user_email"):
            tds.append(HTML.th("Email Address"))
        tds.append(HTML.th("Action"))
        headers.append(HTML.tr(*tds))

        tds = [
            "",  # HTML.input(name="page", type="hidden", value=request.args.get("page", "1")),
            tags.checkbox("avatar", checked=request.args.get("avatar")),
            tags.text("username", value=request.args.get("username")),
            "",
            tags.checkbox("posts", value="1", checked=request.args.get("posts")),
            tags.checkbox("comments", value="1", checked=request.args.get("comments")),
        ]
        if user.can("view_user_email"):
            tds.append(tags.text("email", value=request.args.get("email")))
        tds.append(tags.submit(name="submit", value="Search"))
        headers.append(HTML.tr(HTML.form(*[HTML.td(x) for x in tds], action="#", method="GET")))

        rows = []
        for duser in users:
            assert isinstance(duser, User)
            tds = [
                duser.id,
                duser.get_avatar_html(16),
                HTML.a(duser.username, href=make_link("user/"+duser.username)),
                str(duser.join_date)[:16],
                HTML.a(duser.post_count, href=make_link("post/list/uploaded_by_id=%d/1" % duser.id)),
                duser.comment_count,
            ]
            if user.can("view_user_email"):
                tds.append(duser.email)
            tds.append("")
            rows.append(HTML.tr(*[HTML.td(x) for x in tds]))

        page.add_block(Block(
            "Users",
            HTML.table(HTML.thead(*headers), HTML.tbody(*rows), class_="zebra")
        ))

    ###################################################################
    # Individual User Details
    ###################################################################

    def display_user_page(self, display_user, stats):
        assert isinstance(display_user, User)

        page = context.page
        user = context.user

        page.title = display_user.username + "'s Page"
        page.heading = display_user.username + "'s Page"
        page.add_block(NavBlock())
        page.add_block(Block("Stats", literal("<br>").join(stats), "main", 10))

        if not user.is_anonymous():
            if user.id == display_user.id or user.can("edit_user_info"):
                page.add_block(Block("Options", self.build_options(display_user), "main", 20))

    def display_ip_list(self, uploads, comments):
        # TODO
        pass

    def build_options(self, duser):
        # TODO
        pass
