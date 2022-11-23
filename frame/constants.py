"""Useful constants to use throughout frame and beyond."""

import enum
import pathlib

DEFAULT_SQLITE_LOC = pathlib.Path(__name__).parent.parent / "frame.db"
DEFAULT_SQLITE = f"sqlite:////{DEFAULT_SQLITE_LOC.resolve()}"


class Environments(enum.Enum):
    DEV = "dev"
    PROD = "prod"
    TEST = "test"


ECOBICI_API = "https://apitransporte.buenosaires.gob.ar/ecobici/gbfs/{endpoint}?client_id={client_id}&client_secret={client_secret}"

POOL_SIZE: int = 50
MAX_OVERFLOW: int = 200

STATUS_ENDPOINT = "stationStatus"
STATIONS_ENDPOINT = "stationInformation"

MODEL_RELOAD_SECONDS = 60 * 60 * 24  # Daily reload
