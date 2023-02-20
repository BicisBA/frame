from typing import Tuple
from datetime import datetime

import typer

from frame.config import cfg
from frame.utils import get_logger
from frame.constants import DEFAULT_TEST_SIZE, FrameMetric
from frame.train.eta import ETA_TARGET, ETA_METRICS, ETA_FEATURES, train_eta

logger = get_logger(__name__)

cli = typer.Typer()


@cli.command()
def eta(
    start_date: datetime = typer.Argument(None, formats=["%Y-%m-%d", "%Y-%m-%m %H"]),
    end_date: datetime = typer.Argument(None, formats=["%Y-%m-%d", "%Y-%m-%m %H"]),
    features: Tuple[str] = ETA_FEATURES,
    target: str = ETA_TARGET,
    metrics: Tuple[FrameMetric] = ETA_METRICS,
    mlflow_tracking_uri: str = cfg.mlflow.uri(),
    test_size: float = typer.Option(DEFAULT_TEST_SIZE, min=0.0, max=1.0),
):
    train_eta(
        start_date=start_date,
        end_date=end_date,
        features=features,
        target=target,
        metrics=metrics,
        mlflow_tracking_uri=mlflow_tracking_uri,
        test_size=test_size,
    )


# TODO
@cli.command()
def availability():
    pass
