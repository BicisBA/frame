from datetime import datetime
from typing import Tuple, Callable, Iterable, Optional

from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_absolute_error
from sklearn.base import BaseEstimator, RegressorMixin, clone

from frame.constants import FrameModels
from frame.train.train import train_model

# TODO: move to constants
ETA_FEATURES: Tuple[str] = ("num_bikes_available",)
ETA_TARGET: str = "eta"
ETA_METRICS: Iterable[Callable] = (mean_absolute_error,)


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
    metrics: Optional[Iterable[Callable]] = ETA_METRICS,
):
    estimator = make_pipeline(...)
    train_model(
        FrameModels.ETA,
        estimator,
        features,
        target,
        metrics=metrics,
        start_date=start_date,
        end_date=end_date,
    )
