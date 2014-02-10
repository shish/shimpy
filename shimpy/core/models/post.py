from .meta import *
from shimpy.core.utils import make_link, get_thumbnail_size
from shimpy.core.context import context
from shimpy.core.balance import balance

from urllib import quote


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
    file_size = Column("filesize", Integer, nullable=False, default=0)
    posted = Column(DateTime(timezone=True), nullable=False, default=func.now())
    source = Column(Unicode)
    locked = Column(Boolean, nullable=False, default=False)
    ext = Column(String)

    user = relationship("User")
    tags = relationship("Tag", secondary=map_post_tag, order_by=desc("tags.count"))
    comments = relationship("Comment", order_by="Comment.posted")

    score = Column("numeric_score", Integer, nullable=False, default=0)

    @staticmethod
    def count_pages(search_terms):
        return Post.count_images(search_terms) / int(context.config.get("index_size", 24))

    @staticmethod
    def count_images(search_terms):
        return Post.find_all_images(search_terms).count()

    @staticmethod
    def find_images(offset, limit, search_terms):
        assert isinstance(offset, int)
        assert isinstance(limit, int)
        assert isinstance(search_terms, list)
        return Post.find_all_images(search_terms).offset(offset).limit(limit).all()  # [start:start + offset]

    @staticmethod
    def find_all_images(search_terms):
        db = context.database

        if context.config.get("speed_hax") and len(search_terms) > 3 and not context.user.can("big_search"):
            raise Exception("Anonymous users may only search for up to 3 tags at a time")

        results = db.query(Post)

        for term in search_terms:
            from shimpy.ext.index import SearchTermParseEvent
            negative = term.startswith("-")
            if negative:
                term = term[1:]
            original_results = results
            stpe = SearchTermParseEvent(results, term, negative)
            context.server.send_event(stpe)
            results = stpe.results

            if results == original_results:
                raise Exception("%s not a valid search term" % term)

        results = results.order_by(Post.id.desc())
        results = results.limit(100)  # during dev
        #log.debug("Image search: %s", results)
        return results

    @property
    def thumb_url(self):
        return self.parse_link_template(
            context.config.get(
                "image_tlink",
                "/thumbs/$(hash)s/thumb.jpg"
            ).replace("$", "%")
        )

    @property
    def thumb_size(self):
        return get_thumbnail_size(self.width, self.height)

    @property
    def image_url(self):
        return self.parse_link_template(
            context.config.get(
                "image_ilink",
                "/images/$(hash)s/$(id)s$$20-$$20$(tags)s.$(ext)s"
            ).replace("$", "%")
        )

    @property
    def page_url(self):
        return make_link("post/view/"+str(self.id))

    def parse_link_template(self, tmpl):
        tmpl = tmpl % {
            "id": self.id,
            "hash": self.fingerprint,
            "tags": quote(self.tags_plain_text.encode('utf8')),
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
        return " ".join(sorted([tag.name for tag in self.tags]))

    @property
    def tooltip(self):
        return " ".join(sorted([tag.name for tag in self.tags]))

    @property
    def r34_url(self):
        return "http://rule34.paheal.net/post/view/%d" % (self.id,)

    @property
    def mime_type(self):
        return "image/jpeg"

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
        tag = context.cache.get("tag-object:%s" % repr(name))
        if not tag:
            name = Alias.resolve(name)
            tag = context.database.query(Tag).filter(func.lower(Tag.name) == name.lower()).first()
            context.cache.set("tag-object:%s" % repr(name), tag)
        return tag

    @staticmethod
    def get_or_create(name):
        return Tag.get(name) or Tag(name)

    @staticmethod
    def split(string):
        return string.split()

    def is_plain(self):
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
    posted = Column(DateTime(timezone=True), nullable=False, default=func.now())

    user = relationship("User")
    post = relationship("Post")

    def __init__(self, user, user_ip, body):
        self.user = user
        self.user_ip = user_ip
        self.body = body
