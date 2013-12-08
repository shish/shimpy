from .meta import *


class WikiPage(Base):
    __tablename__ = "wiki_pages"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column("owner_id", Integer, ForeignKey("users.id"), nullable=False)
    # user_ip = Column("owner_ip", postgresql.INET, nullable=False)
    user_ip = Column("owner_ip", String(255), nullable=True)
    title = Column(Unicode, nullable=False)
    body = Column(Unicode, nullable=False)
    revision = Column(Integer, nullable=False, default=1)
    posted = Column("date", DateTime(timezone=True), nullable=False, default=func.now())
    locked = Column(Boolean, nullable=False, default=False)

    user = relationship("User")

    def __repr__(self):
        return "WikiPage(title=%r, revision=%r)" % (self.title, self.revision)
