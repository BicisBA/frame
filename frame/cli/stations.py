import typer

from frame.config import cfg
from frame.data.ecobici import fetch_stations
from frame.models.base import SessionLocal
from frame.models.stations import Station
from frame.utils import get_logger

logger = get_logger(__name__)

cli = typer.Typer()


@cli.command()
def download():
    logger.info("fetching stations from ecobici API")
    stations = fetch_stations()
    logger.info("inserting stations into db")
    db = SessionLocal()
    for station in stations:
        station_id = station.pop("station_id")
        station["id"] = station_id
        station = {k: v for k, v in station.items() if k in Station.__table__.columns.keys()}
        db.add(Station(**station))
    db.commit()
    db.close()
