"""Logic for stations."""
from typing import List

from sqlalchemy.orm import Session

from frame.exceptions import StationDoesNotExist
from frame.models import Station


def get_stations(db: Session) -> List[Station]:
    """Get all stations."""
    return db.query(Station).all()


def get_station(station_id: int, db: Session) -> Station:
    """Get station by id."""
    station = db.query(Station).filter(Station.id == station_id).first()
    if station is None:
        raise StationDoesNotExist()
    return station
