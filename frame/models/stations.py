"""Entity to represent an EcoBici station"""
# pylint: disable=too-few-public-methods

from sqlalchemy import Column, String, Integer, Numeric

from frame.models.base import Base


class Station(Base):
    """An EcoBici station."""

    __tablename__ = "stations"
    station_id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    lat = Column(Numeric)
    lon = Column(Numeric)
    address = Column(String)
    capacity = Column(Integer)


class StationStatus(Base):
    """An EcoBici station status."""

    __tablename__ = "stations_status"
    station_id = Column(Integer, primary_key=True, nullable=False)
    num_bikes_available = Column(Integer, nullable=False)
    num_bikes_disabled = Column(Integer, nullable=False)
    num_docks_available = Column(Integer, nullable=False)
    num_docks_disabled = Column(Integer, nullable=False)
    status = Column(String, nullable=True)
    last_reported = Column(Integer, nullable=True)
