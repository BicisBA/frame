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


class MLFlowStage(str, enum.Enum):
    Staging = "Staging"
    Production = "Production"
    Archived = "Archived"


class FrameModels(str, enum.Enum):
    ETA = "eta"
    AVAILABILITY = "availability"


MODELS_QUERIES = {FrameModels.ETA: "eta", FrameModels.AVAILABILITY: "availability"}
