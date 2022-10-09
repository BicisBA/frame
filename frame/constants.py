"""Useful constants to use throughout frame and beyond."""

import enum
import pathlib

DEFAULT_SQLITE_LOC = pathlib.Path(__name__).parent.parent / "frame.db"
DEFAULT_SQLITE = f"sqlite:////{DEFAULT_SQLITE_LOC.resolve()}"


class Environments(enum.Enum):
    DEV = "dev"
    PROD = "prod"
    TEST = "test"

ECOBICI_API = 'https://apitransporte.buenosaires.gob.ar/ecobici/gbfs/{endpoint}?client_id={client_id}&client_secret={client_secret}'

STATUS_ENDPOINT = 'stationStatus'
STATIONS_ENDPOINT = 'stationInformation'
