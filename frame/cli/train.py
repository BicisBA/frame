from typing import List
from datetime import datetime

import typer

from frame.utils import get_logger
from frame.config import cfg, env as CFG_ENV
from frame.constants import DEFAULT_TEST_SIZE, FrameMetric, Environments
from frame.train.eta import (
    ETA_TARGET,
    ETA_METRICS,
    ETA_CAT_FEATURES,
    ETA_NUM_FEATURES,
    PARTITION_COLUMN,
    train_eta,
)
from frame.train.availability import (
    NEG_WEIGHT as AVAILABILITY_NEG_WEIGHT,
    POS_WEIGHT as AVAILABILITY_POS_WEIGHT,
    AVAILABILITY_TARGET,
    AVAILABILITY_METRICS,
    DEFAULT_MINUTES_TO_EVAL,
    AVAILABILITY_CAT_FEATURES,
    AVAILABILITY_NUM_FEATURES,
    AVAILABILITY_PARTITION_COLUMN,
    train_availability,
)

logger = get_logger(__name__)

cli = typer.Typer()


@cli.command()
def eta(
    start_date: datetime = typer.Argument(..., formats=["%Y-%m-%d", "%Y-%m-%m %H"]),
    end_date: datetime = typer.Argument(..., formats=["%Y-%m-%d", "%Y-%m-%m %H"]),
    num_features: List[str] = ETA_NUM_FEATURES,
    cat_features: List[str] = ETA_CAT_FEATURES,
    target: str = ETA_TARGET,
    metrics: List[FrameMetric] = ETA_METRICS,
    mlflow_tracking_uri: str = cfg.mlflow.uri(),
    test_size: float = typer.Option(DEFAULT_TEST_SIZE, min=0.0, max=1.0),
    partition_column: str = PARTITION_COLUMN,
    env: Environments = CFG_ENV,
):
    train_eta(
        start_date=start_date,
        end_date=end_date,
        num_features=num_features,
        cat_features=cat_features,
        target=target,
        metrics=metrics,
        mlflow_tracking_uri=mlflow_tracking_uri,
        test_size=test_size,
        partition_column=partition_column,
        env=env,
    )


@cli.command()
def availability(
    start_date: datetime = typer.Argument(..., formats=["%Y-%m-%d", "%Y-%m-%m %H"]),
    end_date: datetime = typer.Argument(..., formats=["%Y-%m-%d", "%Y-%m-%m %H"]),
    num_features: List[str] = AVAILABILITY_NUM_FEATURES,
    cat_features: List[str] = AVAILABILITY_CAT_FEATURES,
    target: str = AVAILABILITY_TARGET,
    metrics: List[FrameMetric] = AVAILABILITY_METRICS,
    mlflow_tracking_uri: str = cfg.mlflow.uri(),
    test_size: float = typer.Option(DEFAULT_TEST_SIZE, min=0.0, max=1.0),
    partition_column: str = AVAILABILITY_PARTITION_COLUMN,
    neg_weight: int = AVAILABILITY_NEG_WEIGHT,
    pos_weight: int = AVAILABILITY_POS_WEIGHT,
    env: Environments = CFG_ENV,
    minutes_to_eval: List[int] = DEFAULT_MINUTES_TO_EVAL,
):
    train_availability(
        start_date=start_date,
        end_date=end_date,
        num_features=num_features,
        cat_features=cat_features,
        target=target,
        metrics=metrics,
        mlflow_tracking_uri=mlflow_tracking_uri,
        test_size=test_size,
        partition_column=partition_column,
        neg_weight=neg_weight,
        pos_weight=pos_weight,
        env=env,
        minutes_to_eval=minutes_to_eval,
    )
