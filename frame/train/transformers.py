from typing import Tuple, Union

import holidays
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin, OneToOneFeatureMixin
from sklearn.neighbors import KDTree

from frame.data.ecobici import fetch_stations_info, fetch_stations_status
from frame.utils import get_logger

logger = get_logger(__name__)

class DtypeFixer(OneToOneFeatureMixin, TransformerMixin, BaseEstimator):
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


class AddHolidays(TransformerMixin, BaseEstimator):
    def __init__(
        self, country: str = "AR", by: Union[str, int] = "ts", out: str = "is_holiday"
    ):
        self.country = country
        self.by = by
        self.out = out

    def fit(self, X, y=None):  # pylint: disable=unused-argument
        return self

    def transform(self, X):
        country_holidays = holidays.country_holidays(self.country)
        return X[self.by].dt.date.apply(country_holidays.__contains__).rename(self.out)

    def get_feature_names_out(self):
        pass


def filter_current_stations(df: pd.DataFrame) -> pd.DataFrame:
    stations_status = pd.DataFrame(fetch_stations_status())
    stations_status = stations_status[stations_status.status == "IN_SERVICE"]

    stations_info = pd.DataFrame(fetch_stations_info())

    common_station_ids = (
        set(stations_status.station_id.unique())
        & set(stations_info.station_id.unique())
        & set(df.station_id.unique())
    )
    return df[df.station_id.isin(common_station_ids)]


class AddNearbyStationsData(TransformerMixin, BaseEstimator):
    def __init__(
        self,
        cols: Tuple[str, ...],
        K: int = 10,
        by: Union[str, int] = "station_id",
    ):
        self.K = K
        self.by = by
        self.cols = cols

    def fit(self, X, y=None):  # pylint: disable=unused-argument
        return self

    def get_feature_names_out(self):
        pass

    def transform(self, X):
        if not isinstance(X, pd.DataFrame):
            raise ValueError("Current implementation supports only Dataframes")

        stations_status = pd.DataFrame(fetch_stations_status())
        stations_status = stations_status[stations_status.status == "IN_SERVICE"]

        stations_info = pd.DataFrame(fetch_stations_info())

        common_station_ids = (
            set(stations_status.station_id.unique())
            & set(stations_info.station_id.unique())
            & set(X[self.by].unique())
        )

        stations_status = stations_status[
            stations_status.station_id.isin(common_station_ids)
        ].reset_index(drop=True)
        stations_info = stations_info[
            stations_info.station_id.isin(common_station_ids)
        ].reset_index(drop=True)

        tree = KDTree(stations_info[["lat", "lon"]], metric="l2")

        nearby_stations = tree.query(
            stations_info[["lat", "lon"]],
            k=self.K + 1,
            return_distance=False,
            sort_results=True,
        )[:, 1:]

        nearby_stations = pd.DataFrame(
            nearby_stations, columns=[f"nearby_{i}" for i in range(1, self.K + 1)]
        )

        stations_info = stations_info.join(nearby_stations)

        for i in range(1, self.K + 1):
            stations_info = pd.merge(
                stations_info,
                stations_info[["station_id"]],
                left_on=f"nearby_{i}",
                right_index=True,
                suffixes=("", f"_nearby_{i}"),
                how="left",
            )

        stations_info = stations_info[
            [col for col in stations_info.columns if col.startswith("station_id")]
        ].set_index("station_id")

        _X = pd.merge(X, stations_info, left_on="station_id", right_index=True, how="left")

        nearby_cols = [f"station_id_nearby_{i}" for i in range(1, self.K + 1)]

        for c in nearby_cols: _X[c] = _X[c].astype("uint16")

        _X = _X.sort_values(["ts", "station_id"])

        for i in range(1, self.K + 1): _X = pd.merge_asof(_X,_X[[*self.cols, "station_id", "ts"]],left_on=["ts"],right_on=["ts"],left_by=f"station_id_nearby_{i}",right_by="station_id",suffixes=("", f"__nearby_{i}"),direction="backward",allow_exact_matches=True,).drop(columns=[f"station_id__nearby_{i}"]).rename(columns=lambda x: x.replace("__", "_"))

        diff_cols = []
        for col in self.cols:
            for i in range(1, self.K + 1):
                try:
                    newcol = f"diff_{col}_{i}"
                    _X[newcol] = _X[col].astype("int8") - _X[f"{col}_nearby_{i}"].astype(
                        "int8"
                    )
                    diff_cols.append(newcol)
                except Exception as e:
                    logger.exception(f"Error with {col=} {i=}")
                    breakpoint()

        _X = _X[
            [
                c
                for c in _X.columns
                if c in diff_cols or any(c.startswith(f"{colname}_nearby") for colname in self.cols)
            ]
        ]

        return _X
