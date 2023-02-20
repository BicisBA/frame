from datetime import datetime
from typing import Tuple, Iterable, Optional

from sklearn.pipeline import make_pipeline
from sklearn.base import BaseEstimator, RegressorMixin, clone

from frame.config import cfg
from frame.train.train import train_model
from frame.constants import METRICS_MAPPING, DEFAULT_TEST_SIZE, FrameMetric, FrameModels

# TODO: move to constants
ETA_FEATURES: Tuple[str] = ("num_bikes_available",)
ETA_TARGET: str = "eta"
ETA_METRICS: Tuple[FrameMetric] = (FrameMetric.MAE,)


class ETAByStationEstimator(BaseEstimator, RegressorMixin):
    def __init__(
        self,
        regressor: RegressorMixin,
        partition_column: str,
        partition_values: Iterable,
    ):
        self.regressor = regressor
        self.partition_column = partition_column
        self.partition_values = partition_values
        self.regressors = {
            val: clone(self.regressor()) for val in self.partition_column
        }

    def fit(self, X, y):
        for val, reg in self.regressors.items():
            mask = X[self.partition_column] == val
            reg.fit(X[mask], y[mask])

    def predict(self, X):
        for val in X[self.partition_column].unique():
            X.iloc[X.partition_column == val, "pred"] = self.regressors[val].predict(
                X.iloc[X.partition_column == val]
            )

        preds = X["pred"].copy()
        X.drop(columns=["pred"], inplace=True)
        return preds


def train_eta(
    start_date: datetime,
    end_date: datetime,
    features: Tuple[str] = ETA_FEATURES,
    target: str = ETA_TARGET,
    metrics: Optional[Tuple[FrameMetric]] = ETA_METRICS,
    mlflow_tracking_uri: str = cfg.mlflow.uri(),
    test_size: float = DEFAULT_TEST_SIZE,
):
    estimator = make_pipeline(...)
    train_model(
        FrameModels.ETA,
        estimator,
        features,
        target,
        metrics=(METRICS_MAPPING[m] for m in metrics) if metrics is not None else None,
        start_date=start_date,
        end_date=end_date,
        mlflow_tracking_uri=mlflow_tracking_uri,
        test_size=test_size,
    )
