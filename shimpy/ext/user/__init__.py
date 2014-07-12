from shimpy.core import Extension, Event
from shimpy.core.context import context
from shimpy.core.utils import SparseList, flash_message, make_link, autodate, captcha_check, ReCheck
from shimpy.core.models import User, Image as Post

import hashlib
import re
from time import time
import structlog

log = structlog.get_logger()


class UserBlockBuildingEvent(Event):
    def __init__(self):
        self.parts = SparseList()

    def add_link(self, name, link, position=50):
        self.parts[position] = {"name": name, "link": link}


class UserPageBuildingEvent(Event):
    def __init__(self, user):
        self.display_user = user
        self.stats = SparseList()

    def add_stats(self, html, position):
        self.stats[position] = html


class UserCreationEvent(Event):
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email


class UserDeletionEvent(Event):
    def __init__(self, user_id):
        self.id = user_id


class UserCreationException(Exception):
    pass


class UserManager(Extension):
    """
    Name: User Management
    Author: Shish <webmaster@shishnet.org>
    Description: Allows people to sign up to the website and be managed
    """
    def __init__(self):
        #from mako.template import Template
        #self.theme = Template(filename='shimpy/ext/user/theme.mako')
        from .theme import UserManagerTheme
        self.theme = UserManagerTheme()

    def onInitExt(self, event, config):
        config.set_default("login_signup_enabled", True)
        config.set_default("login_memory", 365)
        config.set_default("avatar_host", "none")
        config.set_default("avatar_gravatar_size", 80)
        config.set_default("avatar_gravatar_default", "")
        config.set_default("avatar_gravatar_rating", "g")
        config.set_default("login_tac_bbcode", True)

    def onPageRequest(self, event, user, send_event, request, config, page, database):
        if user.is_anonymous():
            self.theme.display_login_block()
        else:
            ubbe = send_event(UserBlockBuildingEvent())
            self.theme.display_user_block(user, ubbe.parts)

        if event.page_matches("user_admin/login"):
            username = request.form.get("username")
            password = request.form.get("password")
            if username and password:
                if self.login(username, password):
                    page.mode = "redirect"
                    page.redirect = "user"
                else:
                    self.theme.display_error(401, "Error", "No user with those details was found")
            else:
                self.theme.display_login_page()

        elif event.page_matches("user_admin/recover"):
            u = User.by_name(request.POST["username"])
            if not u:
                self.theme.display_error(404, "Error", "There's no user with that name")
            elif not u.email:
                self.theme.display_error(400, "Error", "That user has no registered email address")
            else:
                pass  # TODO: send email
        elif event.page_matches("user_admin/create"):
            if not config.get_bool("login_signup_enabled"):
                self.theme.display_signups_disabled()
            elif not request.POST["username"]:
                self.theme.display_signup_page()
            elif request.POST["password1"] != request.POST["password2"]:
                self.theme.display_error(400, "Password Mismatch", "Passwords don't match")
            else:
                try:
                    if not captcha_check():
                        raise UserCreationException("Error in captcha")

                    uce = UserCreationEvent(request.POST["name"], request.POST["password1"], request.POST["email"])
                    send_event(uce)
                    self.set_login_cookie(uce.username, uce.password)
                    page.mode = "redirect"
                    page.redirect = make_link("user")
                except UserCreationException as e:
                    self.theme.display_error(400, "User Creation Error", str(e))

        elif event.page_matches("user_admin/list"):
            user_list = database.query(User).order_by(User.id.desc())
            if request.args.get("avatar"):
                user_list = user_list.filter(User.email != "").filter(User.email != None)
            if request.args.get("username"):
                user_list = user_list.filter(User.username.ilike("%" + request.args["username"] + "%"))
            if request.args.get("comments"):
                user_list = user_list.filter(User.comment_count >= int(request.args["comments"]))
            if request.args.get("posts"):
                user_list = user_list.filter(User.post_count >= int(request.args["posts"]))
            if request.args.get("email") and user.can("view_user_email"):
                user_list = user_list.filter(User.email.ilike("%" + request.args["email"] + "%"))

            page = int(request.args.get("page", 1))
            user_list = user_list.offset((page - 1) * 100).limit(100)
            self.theme.display_user_list(user_list, user)

        elif event.page_matches("user_admin/logout"):
            self.logout()

        if not user.check_auth_token():
            return

        elif event.page_matches("user_admin/change_pass"):
            pass  # TODO

        elif event.page_matches("user_admin/change_email"):
            pass  # TODO

        elif event.page_matches("user_admin/change_class"):
            pass  # TODO

        elif event.page_matches("user_admin/delete"):
            pass  # TODO

        elif event.page_matches("user"):
            display_user = User.by_name(event.get_arg(0)) if event.count_args() else user

            if display_user == user and user.is_anonymous():
                self.theme.display_error(
                    page, 401, "Not Logged In",
                    "You aren't logged in. First do that, then you can see your stats."
                )
            elif display_user and not display_user.is_anonymous():
                upbe = UserPageBuildingEvent(display_user)
                send_event(upbe)
                self.display_stats(upbe, user, send_event, config)
            else:
                self.theme.display_error(
                    page, 404, "No Such User",
                    "If you typed the ID by hand, try again; if you came from a link on this "
                    "site, it might be bug report time..."
                )

    def onUserPageBuilding(self, event, config, user):
        h_join_date = autodate(event.display_user.join_date)
        if event.display_user.can("hellbanned"):
            h_class = event.display_user.category.parent.name
        else:
            h_class = event.display_user.category.name

        event.add_stats('User ID: %d' % event.display_user.id, 10)
        event.add_stats("Joined: %s" % h_join_date, 10)
        event.add_stats("Class: %s" % h_class, 90)

        av = event.display_user.get_avatar_html(160)
        if av:
            event.add_stats(av, 0)
        elif config.get_string("avatar_host") == "gravatar" and user.id == event.display_user.id:
            event.add_stats(
                "No avatar? This gallery uses <a href='http://gravatar.com'>Gravatar</a> for avatar "
                "hosting, use the"
                "<br>same email address here and there to have your avatar synced<br>",
                0
            )

    def display_stats(self, event, user, send_event, config):
        self.theme.display_user_page(event.display_user, event.stats)

        if user.id == event.display_user.id:
            ubbe = UserBlockBuildingEvent()
            send_event(ubbe)
            self.theme.display_user_links(user, ubbe.parts)

        if (
            (user.can("view_ip") or (user.is_logged_in() and user.id == event.display_user.id)) and
            (event.display_user.id != config.get_int("anon_id"))
        ):
            self.theme.display_ip_list(
                self.count_upload_ips(event.display_user),
                self.count_comment_ips(event.display_user)
            )

    def onSetupBuilding(self, event, config):
        sb = SetupBlock("User Options")
        sb.add_bool_option("login_signup_enabled", "Allow new signups: ")
        sb.add_longtext_option("login_tac", "<br>Terms &amp; Conditions:<br>")
        sb.add_choice_option(
            "avatar_host",
            [("None", "none"), ("Gravatar", "gravatar")],
            "<br>Avatars: "
        )

        if config.get_string("avatar_host") == "gravatar":
            sb.add_label("<br>&nbsp;<br><b>Gravatar Options</b>")
            sb.add_choice_option("avatar_gravatar_type",
                [
                    ('Default', 'default'),
                    ('Wavatar', 'wavatar'),
                    ('Monster ID', 'monsterid'),
                    ('Identicon', 'identicon'),
                ],
                "<br>Type: "
            )
            sb.add_choice_option(
                "avatar_gravatar_rating",
                [('G', 'g'), ('PG', 'pg'), ('R', 'r'), ('X', 'x')],
                "<br>Rating: "
            )

        sb.add_choice_option(
            "user_loginshowprofile",
            [("return to previous page", 0), ("send to user profile", 1)],
            "<br>When user logs in/out"
        )
        event.panel.add_block(sb)

    def onUserBlockBuilding(self, event):
        event.add_link("My Profile", make_link("user"))
        event.add_link("Log Out", make_link("user_admin/logout"), 99)

    def onUserCreation(self, event):
        self.check_user_creation()
        self.create_user(event)

    def onSearchTermParse(self, event, user):
        r = ReCheck()
        if r.match("/^(poster|user)=(.*)$/i", event.term):
            display_user = User.by_name(r.group(2))
            user_id = display_user.id if display_user else -1
            event.add_filter(Post.user_id == user_id)
        elif r.match("/^(poster|user)_id=(.*)$/i", event.term):
            event.add_filter(Post.user_id == r.group(2))
        elif user.can("view_ip") and r.match("/^(poster|user)_ip=([0-9\.]+)$/i", event.term):
            event.add_filter(Post.user_ip == r.group(2))

    def login(self, username, password):
        hash_ = hashlib.md5(username.lower() + password).hexdigest()
        display_user = User.by_name_and_hash(username, hash_)
        if display_user:
            self.set_login_cookie(display_user.name, password)
            log.info("User logged in", target_user=display_user.name)
        else:
            log.warning("Failed to log in as", target_user=username)
        return display_user

    def logout(self):
        delete_prefixed_cookie("session")
        delete_prefixed_cookie("user")
        log.info("User logged out")

        context.page.mode = "redirect"
        context.page.redirect = make_link()

    def check_user_creation(self, event):
        if not event.username:
            raise UserCreationException("Username is empty")
        elif not re.match("^[a-zA-Z0-9_]+$", event.username):
            raise UserCreationException(
                "Username contains invalid characters. Allowed characters are "
                "letters, numbers, dash, and underscore"
            )
        elif User.by_name(event.username):
            raise UserCreationException("That username is already taken")

    def create_user(self, event):
        pass

    def set_login_cookie(self, username, password):
        addr = get_session_ip()
        hash_ = hashlib.md5(username.lower() + password).hexdigest()
        set_prefixed_cookie("user", username, time()+60*60*24*365, '/')
        set_prefixed_cookie("session", hashlib.md5(hash_ + addr).hexdigest(), time()+60*60*24*config.get_int("login_memory"), '/')

    def _can_user_edit_user(self, a, b):
        if a.is_anonymous():
            self.theme.display_error(page, 401, "Error", "You aren't logged in")

        if a.id == b.id:
            return True

        if b.can("protected"):
            if a.class_.name == "admin":
                return True
            else:
                self.theme.display_error(
                    page, 401, "Error",
                    "You need to be an admin to change other people's details"
                )
        else:
            if a.can("edit_user_info"):
                return True
            else:
                self.theme.display_error(
                    page, 401, "Error",
                    "You need to be an admin to change other people's details"
                )

        return False

    def _redirect_to_user(self, display_user):
        page.mode = "redirect"
        if user.id == display_user.id:
            page.redirect = make_link("user")
        else:
            page.redirect = make_link("user/%s" % display_user.name)

    def _change_password_wrapper(self, display_user, pass1, pass2):
        if self._can_user_edit_user(user, display_user):
            if pass1 != pass2:
                self.theme.display_error(page, 400, "Error", "Passwords don't match")
            else:
                display_user.set_password(pass1)
                if user.id == display_user.id:
                    self._set_login_cookie(user.name, pass1)

                flash_message("Password changed")
                self._redirect_to_user(display_user)

    def _change_email_wrapper(self, display_user, email):
        if self._can_user_edit_user(user, display_user):
            display_user.set_email(email)
            flash_message("Email changed")
            self._redirect_to_user(display_user)

    def _change_class_wrapper(self, display_user, class_):
        if self._can_user_edit_user(user, display_user):
            display_user.set_class(class_)
            flash_message("Email changed")
            self._redirect_to_user(display_user)
