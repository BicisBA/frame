from datetime import datetime
from typing import Tuple, Optional

from lightgbm import LGBMClassifier
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
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


AVAILABILITY_NUM_FEATURES: Tuple[str, ...] = (
    "num_bikes_available",
    "num_bikes_disabled",
    "num_docks_available",
    "num_docks_disabled",
    "minutes_bt_check",
)

AVAILABILITY_CAT_FEATURES: Tuple[str, ...] = ("hod", "dow")

AVAILABILITY_PARTITION_COLUMN: str = "station_id"

AVAILABILITY_TARGET: str = "bikes_available"
AVAILABILITY_METRICS: Tuple[FrameMetric, ...] = (
    FrameMetric.FP,
    FrameMetric.FN,
    FrameMetric.TP,
    FrameMetric.TN,
)

NEG_WEIGHT: int = 500
POS_WEIGHT: int = 1


def train_availability(
    start_date: datetime,
    end_date: datetime,
    num_features: Tuple[str, ...] = AVAILABILITY_NUM_FEATURES,
    cat_features: Tuple[str, ...] = AVAILABILITY_CAT_FEATURES,
    target: str = AVAILABILITY_TARGET,
    metrics: Optional[Tuple[FrameMetric, ...]] = AVAILABILITY_METRICS,
    mlflow_tracking_uri: str = cfg.mlflow.uri(),
    test_size: float = DEFAULT_TEST_SIZE,
    partition_column: str = AVAILABILITY_PARTITION_COLUMN,
    neg_weight: Optional[int] = NEG_WEIGHT,
    pos_weight: Optional[int] = POS_WEIGHT,
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
            LGBMClassifier(
                class_weight={0: neg_weight or 1, 1: pos_weight or 1},
                n_estimators=5,
                max_depth=6,
            ),
            partition_column,
        ),
    )
    pipeline.set_output(transform="pandas")

    train_model(
        FrameModels.AVAILABILITY,
        pipeline,
        num_features,
        cat_features,
        target,
        metrics=(METRICS_MAPPING[m] for m in metrics) if metrics is not None else None,
        start_date=start_date,
        end_date=end_date,
        mlflow_tracking_uri=mlflow_tracking_uri,
        test_size=test_size,
        env=env,
    )
