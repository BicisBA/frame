import youconfigme as ycm
from fastapi import FastAPI
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_utils.tasks import repeat_every
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.backends.inmemory import InMemoryBackend

from frame.config import cfg
from frame import __version__
from frame.utils import get_logger
from frame.models.base import SessionLocal
from frame.constants import MODEL_RELOAD_SECONDS
from frame.api.services import stations as station_service
from frame.api.namespaces.stations import router as stations_router
from frame.api.dependencies import ETAPredictor, AvailabilityPredictor

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
@repeat_every(
    seconds=cfg.api.refresh_stations_info(default=21600, cast=int),
    max_repetitions=None,
    logger=logger,
)
def refresh_stations_info() -> None:
    logger.info("Refreshing stations info")
    db = SessionLocal()
    station_service.update_stations_info(db)
    db.close()


@app.on_event("startup")
@repeat_every(
    seconds=cfg.api.refresh_stations_status(default=30, cast=int),
    max_repetitions=None,
    logger=logger,
)
def refresh_stations_status() -> None:
    logger.info("Refreshing stations status")
    db = SessionLocal()
    station_service.update_stations_status(db)
    db.close()


@app.on_event("startup")
@repeat_every(
    seconds=cfg.models.reload(default=MODEL_RELOAD_SECONDS, cast=int),
    max_repetitions=None,
    logger=logger,
)
def refresh_models() -> None:
    logger.info("Reloading models")
    logger.info("Reloading ETA model")
    ETAPredictor.reload()
    logger.info("Reloading availability model")
    AvailabilityPredictor.reload()
    logger.info("Models reloaded")


@app.on_event("startup")
async def set_redis_cache():
    try:
        redis_url = cfg.redis.url()
        logger.info("Setting cache on redis %s", redis_url)
        redis = aioredis.from_url(redis_url, encoding="utf8", decode_responses=True)
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache-frame")
    except ycm.ConfigItemNotFound:
        logger.info("Setting cache in memory")
        FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache-frame")
