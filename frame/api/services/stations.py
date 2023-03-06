"""Logic for stations."""
from typing import List
from datetime import datetime

from sqlalchemy.orm import Session

from frame.utils import get_logger
from frame.api.dependencies import MLFlowPredictor
from frame.api.schemas.stations import PredictionParams
from frame.models import Station, Prediction, StationStatus
from frame.data.ecobici import fetch_stations_info, fetch_stations_status
from frame.exceptions import (
    PredictionError,
    NoInfoForStation,
    StationDoesNotExist,
    UninitializedPredictor,
)

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
    """Update stations information with the latest data from the API."""
    stations_info = fetch_stations_info()

    columns = Station.__table__.columns.keys()

    for station_info in stations_info:
        new_station: Station
        db_station = (
            db.query(Station)
            .filter(Station.station_id == station_info["station_id"])
            .first()
        )
        if db_station is None:
            new_station = Station(**{col: station_info.get(col) for col in columns})
        else:
            new_station = db_station
            new_station.update_fields(**{col: station_info.get(col) for col in columns})

        db.merge(new_station)
    db.commit()


def update_stations_status(db: Session) -> None:
    """Update stations status with the latest data from the API."""
    stations_status = fetch_stations_status()

    columns = StationStatus.__table__.columns.keys()

    for station_status in stations_status:
        if station_status["status"] == "END_OF_LIFE":
            logger.info("Skipping %s, since it's marked as EOL", station_status)
            continue

        if (
            db.query(Station)
            .filter(Station.station_id == station_status["station_id"])
            .first()
            is None
        ):
            logger.info(
                "Skipping %s, since there's no info for such station", station_status
            )
            continue

        new_station_status: StationStatus

        db_station_status = (
            db.query(StationStatus)
            .filter(StationStatus.station_id == station_status["station_id"])
            .first()
        )
        if db_station_status is None:
            new_station_status = StationStatus(
                **{col: station_status.get(col) for col in columns}
            )
        else:
            new_station_status = db_station_status
            new_station_status.update_fields(
                **{col: station_status.get(col) for col in columns}
            )
        db.merge(new_station_status)
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
    station_id: int,
    prediction_params: PredictionParams,
    db: Session,
    eta_predictor: MLFlowPredictor,
    availability_predictor: MLFlowPredictor,
) -> Prediction:
    """Predict availability of bike in a given station at some point in the future.

    This method not only returns the probability of availability at a given time, but
    also the estimated time of arrival of a bike after said point, were the prediction
    that no bikes will be available by then.
    """

    current_time = datetime.now()
    station_status = get_station_status(station_id, db)

    try:
        eta_features = {
            "station_id": station_id,
            "hod": current_time.hour,
            "dow": (current_time.weekday() + 1) % 7,
            "num_bikes_disabled": station_status.num_bikes_disabled,
            "num_docks_available": station_status.num_docks_available,
            "num_docks_disabled": station_status.num_docks_disabled,
        }
        bike_eta = eta_predictor.predict(**eta_features)
    except UninitializedPredictor:
        logger.exception("Error predicting ETA")
        raise PredictionError("Uninitialized ETA predictor")

    try:
        availability_features = {
            "station_id": station_id,
            "hod": current_time.hour,
            "dow": (current_time.weekday() + 1) % 7,
            "num_bikes_available": station_status.num_bikes_available,
            "num_bikes_disabled": station_status.num_bikes_disabled,
            "num_docks_available": station_status.num_docks_available,
            "num_docks_disabled": station_status.num_docks_disabled,
            "minutes_bt_check": prediction_params.user_eta,
        }
        availability_probability = availability_predictor.predict(
            **availability_features
        )
    except UninitializedPredictor:
        logger.exception("Error predicting availability")
        raise PredictionError("Uninitialized availability predictor")

    new_prediction = Prediction(
        station_id=station_id,
        bike_availability_probability=availability_probability,
        bike_eta=bike_eta,
        user_eta=prediction_params.user_eta,
        user_lat=prediction_params.user_lat,
        user_lon=prediction_params.user_lon,
        eta_model_version=eta_predictor.model_version,
        availability_model_version=availability_predictor.model_version,
        eta_features=eta_features,
        availability_features=availability_features,
    )
    db.add(new_prediction)
    db.commit()
    return new_prediction
