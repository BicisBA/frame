"""Entity to represent an EcoBici station"""
# pylint: disable=too-few-public-methods

from sqlalchemy.sql import func
from sqlalchemy import (
    Float,
    Column,
    String,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
    CheckConstraint,
)

from frame.models.base import Base, UpdatableBase


class Station(Base, UpdatableBase):
    """An EcoBici station."""

    __tablename__ = "stations"
    station_id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    lat = Column(Numeric)
    lon = Column(Numeric)
    address = Column(String)
    capacity = Column(Integer)


class StationStatus(Base, UpdatableBase):
    """An EcoBici station status."""

    __tablename__ = "stations_status"
    station_id = Column(
        Integer, ForeignKey("stations.station_id"), nullable=False, primary_key=True
    )
    num_bikes_available = Column(Integer, nullable=False)
    num_bikes_disabled = Column(Integer, nullable=False)
    num_docks_available = Column(Integer, nullable=False)
    num_docks_disabled = Column(Integer, nullable=False)
    status = Column(String, nullable=True)
    last_reported = Column(Integer, nullable=True)


class Prediction(Base):
    """Prediction made for an user."""

    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, nullable=False)
    station_id = Column(Integer, ForeignKey("stations.station_id"))
    bike_availability_probability = Column(Float, nullable=False)
    availability_model_version = Column(Integer, nullable=True)
    bike_eta = Column(Float, nullable=False)
    eta_model_version = Column(Integer, nullable=True)
    user_eta = Column(Float, nullable=False)
    user_lat = Column(Numeric, nullable=False)
    user_lon = Column(Numeric, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    CheckConstraint(
        "bike_availability_probability >= 0", name="bike_avail_prob_above_zero"
    )
    CheckConstraint(
        "bike_availability_probability <= 1", name="bike_avail_prob_below_one"
    )
    CheckConstraint("bike_eta >= 0", name="bike_eta_above_zero")
