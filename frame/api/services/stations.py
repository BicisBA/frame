"""Logic for stations."""
import operator as ops
from typing import List

import requests
from sqlalchemy.orm import Session

from frame.config import cfg
from frame.constants import ECOBICI_API, STATUS_ENDPOINT, STATIONS_ENDPOINT
from frame.exceptions import NoInfoForStation, StationDoesNotExist
from frame.models import Station, StationStatus
from frame.utils import get_logger

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


def fetch_stations_status() -> List[StationStatus]:
    logger.info("Fetching stations status from API")
    url = ECOBICI_API.format(endpoint=STATUS_ENDPOINT, client_id=cfg.ecobici.client_id(), client_secret=cfg.ecobici.client_secret())
    response = requests.get(url, timeout=120)
    try:
        response.raise_for_status()
        return response.json()['data']['stations']
    except:
        logger.error("Error fetching stations status from API", exc_info=True)
        raise


def fetch_stations_info() -> List[StationStatus]:
    logger.info("Fetching stations information from API")
    url = ECOBICI_API.format(endpoint=STATIONS_ENDPOINT, client_id=cfg.ecobici.client_id(), client_secret=cfg.ecobici.client_secret())
    response = requests.get(url, timeout=120)
    try:
        response.raise_for_status()
        return response.json()['data']['stations']
    except:
        logger.error("Error fetching stations information from API", exc_info=True)
        raise


def update_stations_info(db: Session) -> None:
    stations_info = fetch_stations_info()

    columns = Station.__table__.columns.keys()

    for station_info in stations_info:
        try:
            db.merge(Station(
                **{col: station_info.get(col) for col in columns}
            ))
        except KeyError:
            logger.error("KeyError, where columns are %s and status is %s", columns, station_info)
            raise

    db.commit()


def update_stations_status(db: Session) -> None:
    stations_status = fetch_stations_status()

    columns = StationStatus.__table__.columns.keys()

    for station_status in stations_status:
        try:
            db.merge(StationStatus(
                **{col: station_status.get(col) for col in columns}
            ))
        except KeyError:
            logger.error("KeyError, where columns are %s and status is %s", columns, station_status)
            raise

    db.commit()


def get_stations_status(db: Session) -> List[StationStatus]:
    """Get status for all stations."""
    stations_status = db.query(StationStatus).filter(StationStatus.status == "IN_SERVICE").all()
    return stations_status


def get_station_status(station_id: int, db: Session) -> StationStatus:
    """Get station status by id."""
    station_status = db.query(StationStatus).filter(StationStatus.station_id == station_id).filter(StationStatus.status == "IN_SERVICE").first()
    if station_status is None:
        raise NoInfoForStation()
    return station_status
