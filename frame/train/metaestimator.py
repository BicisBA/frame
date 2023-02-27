from typing import Dict, Union

import numpy as np
from tqdm import tqdm
from sklearn.base import BaseEstimator, RegressorMixin, clone

from frame.utils import get_logger
from frame.constants import FALLBACK_KEY

logger = get_logger(__name__)


class PartitionedMetaEstimator(BaseEstimator, RegressorMixin):
    def __init__(
        self,
        regressor: BaseEstimator,
        partition_column: str,
    ):
        self.regressor = regressor
        self.partition_column = partition_column
        self.regressors: Dict[Union[int, str], BaseEstimator] = {}

    def fit(self, X, y):
        logger.info("Fit fallback estimator")
        self.regressors[FALLBACK_KEY] = clone(self.regressor)
        self.regressors[FALLBACK_KEY].fit(X, y)

        logger.info("Fit stations estimators")
        for val in tqdm(X[self.partition_column].unique(), desc="Fitting"):
            mask = X[self.partition_column] == val

            self.regressors[val] = clone(self.regressor)
            self.regressors[val].fit(X[mask], y[mask])

    def predict(self, X):
        preds = np.empty(len(X))

        for val in X[self.partition_column].unique():
            if val not in self.regressors:
                continue
            mask = X[self.partition_column] == val
            preds[mask] = self.regressors[val].predict(X[mask])

        fallback = ~X[self.partition_column].isin(self.regressors.keys())
        if fallback.sum() > 0:
            preds[fallback] = self.regressors[FALLBACK_KEY].predict(X[fallback])

        return preds
