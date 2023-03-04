from datetime import datetime
from typing import Tuple, Optional

from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from frame.utils import get_logger
from frame.train.train import train_model
from frame.config import cfg, env as CFG_ENV
from frame.train.metaestimator import PartitionedMetaEstimator
from frame.constants import (
    METRICS_MAPPING,
    DEFAULT_TEST_SIZE,
    FrameMetric,
    FrameModels,
    Environments,
)

logger = get_logger(__name__)


ETA_NUM_FEATURES: Tuple[str, ...] = (
    "num_bikes_disabled",
    "num_docks_available",
    "num_docks_disabled",
)

ETA_CAT_FEATURES: Tuple[str, ...] = ("hod", "dow")

PARTITION_COLUMN: str = "station_id"

ETA_TARGET: str = "minutes_bt_check"
ETA_METRICS: Tuple[FrameMetric, ...] = (FrameMetric.MAE,)


def train_eta(
    start_date: datetime,
    end_date: datetime,
    num_features: Tuple[str, ...] = ETA_NUM_FEATURES,
    cat_features: Tuple[str, ...] = ETA_CAT_FEATURES,
    target: str = ETA_TARGET,
    metrics: Optional[Tuple[FrameMetric, ...]] = ETA_METRICS,
    mlflow_tracking_uri: str = cfg.mlflow.uri(),
    test_size: float = DEFAULT_TEST_SIZE,
    partition_column: str = PARTITION_COLUMN,
    env: Environments = CFG_ENV,
):

    pipeline = make_pipeline(
        ColumnTransformer(
            [
                (
                    "ohe",
                    OneHotEncoder(
                        handle_unknown="infrequent_if_exist", sparse_output=False
                    ),
                    [*cat_features],
                ),
                (
                    "ss",
                    StandardScaler(),
                    [*num_features],
                ),
                ("passthrough", "passthrough", [partition_column]),
            ],
            verbose_feature_names_out=False,
        ),
        PartitionedMetaEstimator(
            MLPRegressor((128, 128, 128), max_iter=200), partition_column
        ),
    )
    pipeline.set_output(transform="pandas")

    train_model(
        FrameModels.ETA,
        pipeline,
        num_features,
        cat_features,
        target,
        metrics=(METRICS_MAPPING[m] for m in metrics) if metrics is not None else None,
        start_date=start_date,
        end_date=end_date,
        mlflow_tracking_uri=mlflow_tracking_uri,
        test_size=test_size,
        stratify=partition_column,
        env=env,
    )
