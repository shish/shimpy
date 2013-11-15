from .meta import *
#from votabo.lib.balance import balance


CONF_THUMB_WIDTH = 192
CONF_THUMB_HEIGHT = 192


map_post_tag = Table('image_tags', Base.metadata,
    Column('image_id', Integer, ForeignKey('images.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)


class Post(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column("owner_id", Integer, ForeignKey("users.id"), nullable=False)
    fingerprint = Column("hash", String, nullable=False)
    width = Column(Integer, nullable=False, default=0)
    height = Column(Integer, nullable=False, default=0)
    posted = Column(DateTime, nullable=False, default=func.now())
    source = Column(Unicode)
    locked = Column(Boolean, nullable=False, default=False)

    user = relationship("User")
    tags = relationship("Tag", secondary=map_post_tag, order_by=desc("tags.count"))
    comments = relationship("Comment", order_by="Comment.posted")

    score = Column("numeric_score", Integer, nullable=False, default=0)

    @staticmethod
    def count_pages(search_terms):
        return 1

    @staticmethod
    def find_images(start, offset, search_terms):
        return []

    @property
    def thumb_url(self):
        return self.parse_link_template(
            global_registries.last.settings.get("votabo.thumb_link", "/thumbs/$(hash)s/thumb.jpg").replace("$", "%")
        )

    @property
    def image_url(self):
        return self.parse_link_template(
            global_registries.last.settings.get("votabo.image_link", "/images/$(hash)s/$(id)s$$20-$$20$(tags)s.$(ext)s").replace("$", "%")
        )

    def get_thumb_link(self):
        return ""
    def get_image_link(self):
        return ""
    def get_page_link(self):
        return ""

    def parse_link_template(self, tmpl):
        tmpl = tmpl % {
            "id": self.id,
            "hash": self.fingerprint,
            "tags": self.tags_plain_text,
            #"base": self.,
            "ext": "jpg",  # FIXME
        }
        tmpl = balance(tmpl)
        return tmpl

    @property
    def thumb_width(self):
        return int(max(self.width * self.thumbscale(), CONF_THUMB_WIDTH / 10))

    @property
    def thumb_height(self):
        return int(max(self.height * self.thumbscale(), CONF_THUMB_HEIGHT / 10))

    def thumbscale(self):
        return min(float(CONF_THUMB_WIDTH) / self.width, float(CONF_THUMB_HEIGHT) / self.height)

    # title = Column(Unicode)
    @property
    def title(self):
        return " ".join([tag.name for tag in self.tags])

    @property
    def tags_plain_text(self):
        return " ".join([tag.name for tag in self.tags])

    @property
    def tooltip(self):
        return " ".join([tag.name for tag in self.tags])

    @property
    def r34_url(self):
        return "http://rule34.paheal.net/post/view/%d" % (self.id,)

    def __str__(self):
        return "<Post id=%d>" % (self.id,)


class PostBan(Base):
    __tablename__ = "image_bans"
    id = Column(Integer, primary_key=True, nullable=False)
    fingerprint = Column("hash", String, nullable=False)
    reason = Column(Unicode, nullable=False, default=u'')
    added = Column("date", DateTime(timezone=True), nullable=False, default=func.now())

    # banner = relationship("User", lazy="joined")


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column("tag", Unicode, unique=True, nullable=False)
    count = Column(Integer, nullable=False, default=1)

    posts = relationship("Post", secondary=map_post_tag, order_by=desc("images.id"))

    def __init__(self, name):
        self.name = name

    @property
    def category(self):
        return "general"

    def __str__(self):
        return "<Tag id=%d name=%s count=%d>" % (self.id, self.name, self.count)

    def __repr__(self):
        return "Tag(%r)" % self.name

    def __json__(self, request=None):
        return {"name": self.name, "count": self.count}

    def __eq__(self, other):
        return (
            (isinstance(other, Tag) and self.name == other.name) or
            (isinstance(other, dict) and self.__json__() == other)
        )

    @staticmethod
    def get(name):
        name = Alias.resolve(name)
        return DBSession.query(Tag).filter(Tag.name.ilike(name)).first()

    @staticmethod
    def get_or_create(name):
        return Tag.get(name) or Tag(name)

    @staticmethod
    def split(string):
        return string.split()

    def is_plain_tag(self):
        """
        If this is a regular tag

        (It might be a metadata search item, eg "width=1024", or an alias)
        """
        return True


class Alias(Base):
    __tablename__ = 'aliases'
    oldtag = Column(Unicode, primary_key=True, nullable=False)
    newtag = Column(Unicode, index=True, nullable=False)

    def __init__(self, oldtag, newtag):
        self.oldtag = oldtag
        self.newtag = newtag

    @staticmethod
    def resolve(name):
        alias = DBSession.query(Alias).filter(Alias.oldtag.ilike(name)).first()
        return alias.newtag if alias else name


class UnTag(Base):
    __tablename__ = 'untags'
    tag = Column(Unicode, primary_key=True, nullable=False)
    redirect = Column(Unicode, index=True, nullable=False)

    def __init__(self, tag, redirect):
        self.tag = tag
        self.redirect = redirect


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column("owner_id", Integer, ForeignKey("users.id"), nullable=False)
    user_ip = Column("owner_ip", String(255), nullable=False)
    post_id = Column("image_id", Integer, ForeignKey("images.id"), nullable=False)
    body = Column("comment", Unicode, nullable=False)
    posted = Column(DateTime, nullable=False, default=func.now())

    user = relationship("User")
    post = relationship("Post")

    def __init__(self, user, user_ip, body):
        self.user = user
        self.user_ip = user_ip
        self.body = body
