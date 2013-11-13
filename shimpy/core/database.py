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


def connect(config):
    log.info("Connecting to database")
    engine = create_engine(config.get("database", "dsn"), echo=False)
    session_factory.configure(bind=engine)

    log.info("Checking connection")
    Session().execute("SELECT 1")
    Session.remove()

    log.info("Creating tables")
    Base.metadata.create_all(engine)
