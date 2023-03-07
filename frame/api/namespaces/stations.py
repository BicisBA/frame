from typing import List

from sqlalchemy.orm import Session
from fastapi_cache.decorator import cache
from fastapi import Depends, APIRouter, HTTPException

from frame.utils import get_logger
from frame.api.schemas import stations as station_schemas
from frame.api.services import stations as station_service
from frame.exceptions import PredictionError, NoInfoForStation, StationDoesNotExist
from frame.api.dependencies import (
    ETAPredictor,
    MLFlowPredictor,
    AvailabilityPredictor,
    get_db,
)

logger = get_logger(__name__)

router = APIRouter(
    prefix="/stations",
    tags=["stations"],
)


@router.get("", response_model=List[station_schemas.Station])
@cache(expire=300)
def get_stations(db: Session = Depends(get_db)):
    return station_service.get_stations(db)


@router.get("/status", response_model=List[station_schemas.StationStatus])
@cache(expire=10)
def get_stations_status(db: Session = Depends(get_db)):
    return station_service.get_stations_status(db)


@router.get("/{station_id}", response_model=station_schemas.Station)
@cache(expire=300)
def get_station(station_id: int, db: Session = Depends(get_db)):
    try:
        return station_service.get_station(station_id, db)
    except StationDoesNotExist:
        raise HTTPException(status_code=404, detail="Station does not exist")


@router.get("/{station_id}/status", response_model=station_schemas.StationStatus)
@cache(expire=10)
def get_station_status(station_id: int, db: Session = Depends(get_db)):
    try:
        return station_service.get_station_status(station_id, db)
    except StationDoesNotExist:
        raise HTTPException(status_code=404, detail="Station does not exist")


@router.post("/{station_id}/prediction", response_model=station_schemas.Prediction)
def predict_for_station(
    station_id: int,
    prediction_params: station_schemas.PredictionParams,
    db: Session = Depends(get_db),
    eta_predictor: MLFlowPredictor = Depends(lambda: ETAPredictor),
    availability_predictor: MLFlowPredictor = Depends(lambda: AvailabilityPredictor),
):
    try:
        return station_service.predict(
            station_id,
            prediction_params,
            db,
            eta_predictor=eta_predictor,
            availability_predictor=availability_predictor,
        )
    except StationDoesNotExist:
        raise HTTPException(status_code=404, detail="Station does not exist")
    except NoInfoForStation:
        raise HTTPException(
            status_code=404,
            detail="There is no information for this station. Probably does not exist.",
        )
    except PredictionError:
        raise HTTPException(status_code=503, detail="Predictor uninitialized")
