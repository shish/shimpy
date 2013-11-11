from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

import logging

log = logging.getLogger(__name__)

session_factory = sessionmaker()
Session = scoped_session(session_factory)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column("name", String)
    password = Column("pass", String)

    def __repr__(self):
       return "<User(username=%r, password=%r)>" % (self.username, self.password)


def connect(config):
    log.info("Connecting to database")
    engine = create_engine(config.get("database", "dsn"), echo=False)
    session_factory.configure(bind=engine)

    log.info("Checking connection")
    Session().execute("SELECT 1")
    Session.remove()

    log.info("Creating tables")
    Base.metadata.create_all(engine)
