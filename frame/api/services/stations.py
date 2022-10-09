"""Logic for stations."""
from typing import List

from sqlalchemy.orm import Session

from frame.utils import get_logger
from frame.models import Station, StationStatus
from frame.exceptions import NoInfoForStation, StationDoesNotExist
from frame.data.ecobici import fetch_stations_info, fetch_stations_status

logger = get_logger(__name__)


def get_stations(db: Session) -> List[Station]:
    """Get all stations."""
    return db.query(Station).all()


def get_station(station_id: int, db: Session) -> Station:
    """Get station by id."""
    station = db.query(Station).filter(Station.station_id == station_id).first()
    if station is None:
        raise StationDoesNotExist()
    return station


def update_stations_info(db: Session) -> None:
    stations_info = fetch_stations_info()

    columns = Station.__table__.columns.keys()

    for station_info in stations_info:
        try:
            db.merge(Station(**{col: station_info.get(col) for col in columns}))
        except KeyError:
            logger.error(
                "KeyError, where columns are %s and status is %s", columns, station_info
            )
            raise

    db.commit()


def update_stations_status(db: Session) -> None:
    stations_status = fetch_stations_status()

    columns = StationStatus.__table__.columns.keys()

    for station_status in stations_status:
        try:
            db.merge(StationStatus(**{col: station_status.get(col) for col in columns}))
        except KeyError:
            logger.error(
                "KeyError, where columns are %s and status is %s",
                columns,
                station_status,
            )
            raise

    db.commit()


def get_stations_status(db: Session) -> List[StationStatus]:
    """Get status for all stations."""
    stations_status = (
        db.query(StationStatus).filter(StationStatus.status == "IN_SERVICE").all()
    )
    return stations_status


def get_station_status(station_id: int, db: Session) -> StationStatus:
    """Get station status by id."""
    station_status = (
        db.query(StationStatus)
        .filter(StationStatus.station_id == station_id)
        .filter(StationStatus.status == "IN_SERVICE")
        .first()
    )
    if station_status is None:
        raise NoInfoForStation()
    return station_status
