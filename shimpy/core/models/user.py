from .meta import *


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    username = Column("name", Unicode, unique=True, nullable=False)
    password = Column("pass", String, nullable=False)
    joindate = Column(DateTime, nullable=False, default=func.now())
    email = Column(String, nullable=True)
    category = Column("class", String, nullable=False)

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

    def get_avatar_url(self, size=80):
        default = ""
        if self.email:
            h = md5(self.email).hexdigest()
            rating = "pg"
            cb = ""
            return "http://www.gravatar.com/avatar/%s.jpg?s=%d&d=%s&r=%s&cacheBreak=%s" % (h, size, default, rating, cb)
        else:
            return default

    def __str__(self):
        return "<User id=%d username=%s>" % (self.id, self.username)

    def set_password(self, password):
        self.password = md5(self.username.lower() + password).hexdigest()

    def check_password(self, password):
        return self.password == md5(self.username.lower() + password).hexdigest()

    @staticmethod
    def by_name(username):
        if username:
            return DBSession.query(User).filter(User.username == username).first()

    @staticmethod
    def by_session(request, username, session):
        duser = User.by_name(username)
        if duser and md5(duser.password + request.remote_addr).hexdigest() == session:
            return duser


class PrivateMessage(Base):
    __tablename__ = "private_message"
    id = Column(Integer, primary_key=True, nullable=False)
    user_from_id = Column("from_id", Integer, ForeignKey("users.id"), nullable=False)
    user_to_id = Column("to_id", Integer, ForeignKey("users.id"), nullable=False)
    sent_date = Column(DateTime, nullable=False, default=func.now())
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
