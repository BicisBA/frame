from typing import List

from sqlalchemy.orm import Session
from fastapi_utils.tasks import repeat_every
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi import Depends, FastAPI, HTTPException

from frame.utils import get_logger
from frame.models.base import SessionLocal
from frame.exceptions import StationDoesNotExist
from frame.api.schemas import stations as station_schemas
from frame.api.services import stations as station_service

logger = get_logger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=256)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
@repeat_every(seconds=86400, max_repetitions=1, logger=logger)
def refresh_stations_info() -> None:
    logger.info("Refreshing stations info")
    db = SessionLocal()
    station_service.update_stations_info(db)
    db.close()


@app.on_event("startup")
@repeat_every(seconds=30, max_repetitions=1, logger=logger)
def refresh_stations_status() -> None:
    logger.info("Refreshing stations status")
    db = SessionLocal()
    station_service.update_stations_status(db)
    db.close()


@app.get("/stations", response_model=List[station_schemas.Station])
def get_stations(db: Session = Depends(get_db)):
    return station_service.get_stations(db)


@app.get("/stations/status", response_model=List[station_schemas.StationStatus])
def get_stations_status(db: Session = Depends(get_db)):
    return station_service.get_stations_status(db)


@app.get("/stations/{station_id}", response_model=station_schemas.Station)
def get_station(station_id: int, db: Session = Depends(get_db)):
    try:
        return station_service.get_station(station_id, db)
    except StationDoesNotExist:
        raise HTTPException(status_code=404, detail="Station does not exist")


@app.get("/stations/{station_id}/status", response_model=station_schemas.StationStatus)
def get_station_status(station_id: int, db: Session = Depends(get_db)):
    try:
        return station_service.get_station_status(station_id, db)
    except StationDoesNotExist:
        raise HTTPException(status_code=404, detail="Station does not exist")


@app.post(
    "/stations/{station_id}/prediction", response_model=station_schemas.Prediction
)
def predict_for_station(
    station_id: int,
    prediction_params: station_schemas.PredictionParams,
    db: Session = Depends(get_db),
):
    try:
        return station_service.predict(station_id, prediction_params, db)
    except StationDoesNotExist:
        raise HTTPException(status_code=404, detail="Station does not exist")
