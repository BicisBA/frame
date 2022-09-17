"""Base object to declare all ORM classes"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from frame.config import cfg
from frame.utils import get_logger
from frame.constants import DEFAULT_SQLITE

logger = get_logger(__name__)

DB_URL = cfg.database.url(default=DEFAULT_SQLITE)
DB_CONN_ARGS = {"check_same_thread": False} if DB_URL == DEFAULT_SQLITE else {}

engine = create_engine(DB_URL, connect_args=DB_CONN_ARGS)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class UpdatableBase:
    def update_fields(self, **kwargs):
        for field, val in kwargs.items():
            setattr(self, field, val)
