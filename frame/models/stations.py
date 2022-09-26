"""Entity to represent an EcoBici station"""
# pylint: disable=too-few-public-methods

from sqlalchemy import Column, String, Boolean, Integer, Numeric, DateTime
from sqlalchemy.sql import func

from frame.models.base import Base


class Station(Base):
    """An EcoBici station."""

    __tablename__ = "stations"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    lat = Column(Numeric)
    lon = Column(Numeric)
    address = Column(String)
    capacity = Column(Integer)
