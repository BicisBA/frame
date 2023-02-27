from typing import List
from datetime import datetime

import typer

from frame.config import cfg
from frame.utils import get_logger
from frame.constants import DEFAULT_TEST_SIZE, FrameMetric
from frame.train.eta import (
    ETA_TARGET,
    ETA_METRICS,
    ETA_CAT_FEATURES,
    ETA_NUM_FEATURES,
    PARTITION_COLUMN,
    train_eta,
)
from frame.train.availability import (
    POS_WEIGHT as AVAILABILITY_POS_WEIGHT,
    AVAILABILITY_TARGET,
    AVAILABILITY_METRICS,
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
    pos_weight: int = AVAILABILITY_POS_WEIGHT,
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
        pos_weight=pos_weight,
    )
