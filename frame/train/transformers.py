import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin, OneToOneFeatureMixin


class CategoryDtypeFixer(OneToOneFeatureMixin, TransformerMixin, BaseEstimator):
    def __init__(self, dtype: str):
        self.dtype = dtype

    def fit(self, X, y=None):  # pylint: disable=unused-argument
        return self

    def transform(self, X):
        if isinstance(X, pd.DataFrame):
            for col in X.columns:
                X[col] = X[col].astype(self.dtype)
        else:
            X = X.astype(self.dtype)
        return X
