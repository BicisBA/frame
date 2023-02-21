from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from frame import __version__
from frame.utils import get_logger
from frame.models.base import SessionLocal
from frame.api.dependencies import ETAPredictor
from frame.constants import MODEL_RELOAD_SECONDS
from frame.api.services import stations as station_service
from frame.api.namespaces.stations import router as stations_router

logger = get_logger(__name__)

app = FastAPI(
    title="Frame - BicisBA API",
    description="Stations, status and predictions for the EcoBici system in Buenos Aires.",
    version=__version__,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=256)
app.include_router(stations_router)


@app.on_event("startup")
@repeat_every(seconds=86400, max_repetitions=None, logger=logger)
def refresh_stations_info() -> None:
    logger.info("Refreshing stations info")
    db = SessionLocal()
    station_service.update_stations_info(db)
    db.close()


@app.on_event("startup")
@repeat_every(seconds=30, max_repetitions=None, logger=logger)
def refresh_stations_status() -> None:
    logger.info("Refreshing stations status")
    db = SessionLocal()
    station_service.update_stations_status(db)
    db.close()


@app.on_event("startup")
@repeat_every(
    seconds=MODEL_RELOAD_SECONDS,
    max_repetitions=None,
    logger=logger,
)
def refresh_models() -> None:
    logger.info("Reloading models")
    logger.info("Reloading ETA model")
    ETAPredictor.reload()
    logger.info("Models reloaded")
