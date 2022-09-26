import secrets
from typing import List

from fastapi import Depends, FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from frame.api.schemas import stations as station_schemas
from frame.api.services import stations as station_service
from frame.config import cfg
from frame.constants import Environments
from frame.exceptions import StationDoesNotExist
from frame.models.base import SessionLocal
from frame.utils import get_logger

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


@app.get("/hello")
def say_hi():
    return JSONResponse(status_code=200, content={"message": "hi"})


@app.get("/stations", response_model=List[station_schemas.Station])
def get_stations(db: Session = Depends(get_db)):
    return station_service.get_stations(db)


@app.get("/stations/{station_id}", response_model=station_schemas.Station)
def get_station(station_id: int, db: Session = Depends(get_db)):
    try:
        return station_service.get_station(station_id, db)
    except StationDoesNotExist:
        raise HTTPException(status_code=404, detail="Station does not exist")
