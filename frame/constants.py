"""Useful constants to use throughout frame and beyond."""

import enum
import pathlib
from typing import Dict, Callable

from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    mean_absolute_percentage_error,
)

from frame.train.metrics import fn, fp, tn, tp

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


class FrameMetric(str, enum.Enum):
    MAPE = "MAPE"
    MAE = "MAE"
    MSE = "MSE"
    FN = "FN"
    FP = "FP"
    TN = "TN"
    TP = "TP"


METRICS_MAPPING: Dict[FrameMetric, Callable] = {
    FrameMetric.MAE: mean_absolute_error,
    FrameMetric.MSE: mean_squared_error,
    FrameMetric.MAPE: mean_absolute_percentage_error,
    FrameMetric.FN: fn,
    FrameMetric.FP: fp,
    FrameMetric.TN: tn,
    FrameMetric.TP: tp,
}

DEFAULT_TEST_SIZE: float = 0.1

FALLBACK_KEY: str = "fallback"

MODEL_RELOAD_SECONDS: int = 60 * 5

JOBLIB_COMPRESSION_ALGORITHM: str = "lzma"
JOBLIB_COMPRESSION_LEVEL: int = 3
