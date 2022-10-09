"""Logic for stations."""
import random
from typing import List

from sqlalchemy.orm import Session

from frame.utils import get_logger
from frame.api.schemas.stations import PredictionParams
from frame.models import Station, Prediction, StationStatus
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


def predict(
    station_id: int, prediction_params: PredictionParams, db: Session
) -> Prediction:
    """Predict availability of bike in a given station at some point in the future.

    This method not only returns the probability of availability at a given time, but
    also the estimated time of arrival of a bike after said point, were the prediction
    that no bikes will be available by then.
    """

    # The following method is locally defined because it should be used only
    # for the mocked prediction
    def clip(x, low, high):
        """Clip x between low and high."""
        x = max(x, low)
        x = min(x, high)
        return x

    bike_availability_probability: float = clip(random.normalvariate(0.5, 0.15), 0, 1)
    bike_eta: float = clip(random.normalvariate(12, 2), 0, 30)

    new_prediction = Prediction(
        station_id=station_id,
        bike_availability_probability=bike_availability_probability,
        bike_eta=bike_eta,
        user_eta=prediction_params.user_eta,
        user_lat=prediction_params.user_lat,
        user_lon=prediction_params.user_lon,
    )
    db.add(new_prediction)
    db.commit()
    return new_prediction
