from .meta import *
import hashlib
from time import time
from webhelpers.html import HTML
import bcrypt


user_classes = {}


class UserClass(object):
    def __init__(self, name, parent, abilities):
        self.name = name
        self.parent = user_classes.get(parent)
        self.abilities = abilities

        user_classes[name] = self

    def can(self, ability):
        if ability in self.abilities:
            return self.abilities[ability]
        elif self.parent:
            return self.parent.can(ability)
        else:
            raise Exception("Unknown permission: %r" % ability)


UserClass("base", None, {
    "hellbanned": False,
    "view_ip": False,
    "view_user_email": False,
    "manage_blocks": False,
    "manage_alias_list": False,
})
UserClass("anonymous", "base", {})
UserClass("user", "base", {})
UserClass("admin", "base", {
    "view_ip": True,
    "view_user_email": True,
})
UserClass("admin-nb", "admin", {})


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    username = Column("name", Unicode, unique=True, nullable=False)
    password = Column("pass", String, nullable=False)
    join_date = Column("joindate", DateTime(timezone=True), nullable=False, default=func.now())
    email = Column(String, nullable=True)
    class_name = Column("class", String, nullable=False)

    # self_description = Column(Unicode, nullable=False, default=u'')
    # admin_description = Column(Unicode, nullable=False, default=u'')

    post_count = Column("image_count", Integer, nullable=False, default=0)
    comment_count = Column("comment_count", Integer, nullable=False, default=0)

    posts = relationship("Post", order_by=desc("images.id"))
    comments = relationship("Comment", order_by=desc("comments.id"))
    pm_inbox = relationship("PrivateMessage", foreign_keys="PrivateMessage.user_to_id")
    pm_outbox = relationship("PrivateMessage", foreign_keys="PrivateMessage.user_from_id")

    ip = "0.0.0.0"  # dynamically set on each request

    def is_anonymous(self):
        return self.username == "Anonymous"

    def is_logged_in(self):
        return not self.is_anonymous()

    def check_auth_token(self):
        # TODO
        return True

    def can(self, perm):
        return user_classes[self.class_name].can(perm)

    @property
    def category(self):
        return user_classes[self.class_name]

    def get_avatar_url(self, size=80):
        default = ""
        if self.email:
            h = hashlib.md5(self.email).hexdigest()
            rating = "pg"
            cb = str(int(time() / (60 * 60 * 24)))
            return "http://www.gravatar.com/avatar/%s.jpg?s=%d&d=%s&r=%s&cacheBreak=%s" % (h, size, default, rating, cb)
        else:
            return default

    def get_avatar_html(self, size=80):
        av = self.get_avatar_url(size)
        if av:
            return HTML.img(src=av, width=size, height=size)
        else:
            return ""

    def __str__(self):
        return "<User id=%d username=%s>" % (self.id, self.username)

    def set_password(self, password):
        self.password = bcrypt.hashpw(password, bcrypt.gensalt())

    def check_password(self, password):
        # Compat for old passwords
        if md5(self.username.lower() + password).hexdigest() == self.password:
            self.set_password(password)

        try:
            # some other libraries (PHP...) use 2y as the version string, when 2a
            # is the standard...
            two_a_pass = self.password.replace("$2y$", "$2a$")
            return bcrypt.hashpw(password, two_a_pass) == two_a_pass
        except ValueError:
            return False  # invalid salt -- stored password /was/ md5, but entered password wasn't correct

    @staticmethod
    def by_name(username):
        if username:
            return DBSession.query(User).filter(User.username == username).first()

    @staticmethod
    def by_request(request):
        return User.by_session(request, request.cookies.get("shm_user"), request.cookies.get("shm_session"))

    @staticmethod
    def by_session(request, username, session):
        from shimpy.core.utils import get_session_ip
        duser = User.by_name(username)
        addr = get_session_ip(request.access_route[0] if request.access_route else request.remote_addr)
        if duser and hashlib.md5(duser.password + addr).hexdigest() == session:
            return duser
        else:
            return User.by_name(u"Anonymous")


class PrivateMessage(Base):
    __tablename__ = "private_message"
    id = Column(Integer, primary_key=True, nullable=False)
    user_from_id = Column("from_id", Integer, ForeignKey("users.id"), nullable=False)
    user_to_id = Column("to_id", Integer, ForeignKey("users.id"), nullable=False)
    sent_date = Column(DateTime(timezone=True), nullable=False, default=func.now())
    subject = Column(Unicode, nullable=False)
    message = Column(Unicode, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)

    user_from = relationship("User", foreign_keys="PrivateMessage.user_from_id", lazy="joined")
    user_to = relationship("User", foreign_keys="PrivateMessage.user_to_id")

    def __str__(self):
        return "<PrivateMessage from=%s to=%s subject=%s>" % (self.user_from.username, self.user_to.username, self.subject)


class IPBan(Base):
    __tablename__ = "bans"
    id = Column(Integer, primary_key=True, nullable=False)
    banner_id = Column("banner_id", Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(Unicode, nullable=False, default=u'')
    until = Column("end_timestamp", Integer, nullable=False, default=0)  # FIXME: datetime(tz=true)
    # ip = Column(postgresql.INET, nullable=False)
    ip = Column(String(255), nullable=False)
    added = Column(DateTime(timezone=True), nullable=False, default=func.now())

    banner = relationship("User", lazy="joined")
