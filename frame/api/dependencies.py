"""Endpoints dependencies."""
from frame.models.base import SessionLocal


def get_db():
    """Get a connection to the DB."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
