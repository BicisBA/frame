from io import BytesIO
from typing import List
from dataclasses import dataclass
from abc import ABC, abstractmethod

import joblib

from frame.s3 import S3Client
from frame.utils import get_logger
from frame.models import StationStatus

logger = get_logger(__name__)

BUCKET = "frame"
CURRENT_AVAILABILITY_KEY = "models/current_availability_model.txt"
CURRENT_ETA_KEY = "models/current_eta_model.txt"


class AvailabilityPredictor(ABC):
    @abstractmethod
    def predict_proba(self, features: List[List]) -> List[List]:
        """Returns the probability of bicycle availability.

        Args:
            features (List[List]): [["hour", "dow", "num_bikes_available",
            "num_bikes_disabled", "num_docks_available", "num_docks_disabled",
             "minutes_bt_check"]]
        Returns:
            List[List]: [[not available probability, available probability]]
        """


class ETAPredictor(ABC):
    @abstractmethod
    def predict(self, features: List[List]) -> List:
        """Returns the expected number of minutes for a bicycle arrival.

        Args:
            features (List[List]): [["hour", "dow", "num_bikes_disabled",
            "num_docks_available", "num_docks_disabled"]]
        Returns:
            List: number of minutes for a bicycle arrival
        """


@dataclass(frozen=True)
class AvailabilityPredictionFeatures:
    station_id: int
    hour: int
    dow: int
    station_status: StationStatus
    minutes_bt_check: int


@dataclass(frozen=True)
class ETAPredictionFeatures:
    station_id: int
    hour: int
    dow: int
    station_status: StationStatus


class Predictors:
    _instance = None
    _s3_client: S3Client
    _availability_predictor: AvailabilityPredictor
    _availability_predictor_key: str = ""
    _eta_predictor: ETAPredictor
    _eta_predictor_key: str = ""

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Predictors, cls).__new__(cls)
            cls._instance._s3_client = S3Client()
        return cls._instance

    def reload_models(self):
        last_availability_predictor_key = (
            self._s3_client.client.Bucket(BUCKET)
            .Object(CURRENT_AVAILABILITY_KEY)
            .get()["Body"]
            .read()
            .decode()
        )
        if self._availability_predictor_key != last_availability_predictor_key:
            with BytesIO() as mem_f:
                self._s3_client.client.Bucket(BUCKET).download_fileobj(
                    Key=last_availability_predictor_key, Fileobj=mem_f
                )
                mem_f.seek(0)
                self._availability_predictor = joblib.load(mem_f)
            self._availability_predictor_key = last_availability_predictor_key
            logger.info(
                "New availability model loaded '%s'", last_availability_predictor_key
            )
        else:
            logger.info(
                "Current availability model '%s' is up to date!",
                last_availability_predictor_key,
            )

        last_eta_predictor_key = (
            self._s3_client.client.Bucket(BUCKET)
            .Object(CURRENT_ETA_KEY)
            .get()["Body"]
            .read()
            .decode()
        )
        if self._eta_predictor_key != last_eta_predictor_key:
            with BytesIO() as mem_f:
                self._s3_client.client.Bucket(BUCKET).download_fileobj(
                    Key=last_eta_predictor_key, Fileobj=mem_f
                )
                mem_f.seek(0)
                self._eta_predictor = joblib.load(mem_f)
            self._eta_predictor_key = last_eta_predictor_key
            logger.info("New eta model loaded '%s'", last_eta_predictor_key)
        else:
            logger.info("Current eta model '%s' is up to date!", last_eta_predictor_key)

    def predict_availability(
        self,
        availability_features: AvailabilityPredictionFeatures,
    ):
        features = [
            [
                availability_features.hour,
                availability_features.dow,
                availability_features.station_status.num_bikes_available,
                availability_features.station_status.num_bikes_disabled,
                availability_features.station_status.num_docks_available,
                availability_features.station_status.num_docks_disabled,
                availability_features.minutes_bt_check,
            ]
        ]
        # return self._availability_predictor[availability_features.station_id].predict_proba(features)[0][1]
        return self._availability_predictor.predict_proba(features)[0][1]

    def predict_eta(
        self,
        eta_features: ETAPredictionFeatures,
    ):
        features = [
            [
                eta_features.hour,
                eta_features.dow,
                eta_features.station_status.num_bikes_disabled,
                eta_features.station_status.num_docks_available,
                eta_features.station_status.num_docks_disabled,
            ]
        ]
        # return self._eta_predictor[eta_features.station_id].predict(features)[0]
        return self._eta_predictor.predict(features)[0]
