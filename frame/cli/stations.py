import typer

from frame.utils import get_logger
from frame.models.base import SessionLocal
from frame.api.services.stations import update_stations_info, update_stations_status

logger = get_logger(__name__)

cli = typer.Typer()


@cli.command()
def update_info():
    db = SessionLocal()
    update_stations_info(db)


@cli.command()
def update_status():
    db = SessionLocal()
    update_stations_status(db)
