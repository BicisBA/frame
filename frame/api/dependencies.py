"""Endpoints dependencies."""
import os
import operator as ops
from typing import List, Union, Optional

import joblib
import mlflow
import pandas as pd
from sklearn.pipeline import Pipeline
from mlflow.tracking import MlflowClient

from frame.config import cfg
from frame.ycm_casts import s3_or_local
from frame.models.base import SessionLocal
from frame.utils import with_env, get_logger
from frame.exceptions import UninitializedPredictor
from frame.constants import FrameModels, MLFlowStage

logger = get_logger(__name__)


def get_db():
    """Get a connection to the DB."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class MLFlowPredictor:
    def __init__(
        self,
        model: FrameModels,
        tracking_uri: str = cfg.mlflow.uri(),
        probabilistic: bool = False,
    ):
        self.model = model
        self.tracking_uri = tracking_uri
        self.pipeline: Optional[Pipeline] = None
        self.model_version: Optional[int] = None
        self.probabilistic = probabilistic

    @property
    def initialized(self):
        return self.pipeline is not None

    @with_env(
        MLFLOW_TRACKING_USERNAME=cfg.mlflow.username(),
        MLFLOW_TRACKING_PASSWORD=cfg.mlflow.password(),
        MLFLOW_TRACKING_SERVER_CERT_PATH=cfg.mlflow.cert_path(cast=s3_or_local),
    )
    def reload(self, stage: MLFlowStage = MLFlowStage.Production) -> None:
        try:
            mlflow.set_tracking_uri(self.tracking_uri)
            client = MlflowClient(self.tracking_uri)

            versions: List[
                mlflow.entities.model_registry.ModelVersion
            ] = client.get_latest_versions(self.model, [stage.value])

            if not versions:
                raise ValueError("No latest models found")

            latest: mlflow.entities.model_registry.ModelVersion = max(
                versions, key=ops.attrgetter("creation_timestamp")
            )

            if self.model_version is not None and self.model_version == latest.version:
                logger.info("Already at latest model for %s", self.model)
                return

            logger.info(
                "Current loaded version is %s, but latest is %s. Downloading from run_id %s",
                self.model_version,
                latest.version,
                latest.run_id,
            )

            latest_path = mlflow.artifacts.download_artifacts(
                artifact_path=f"{self.model}.joblib", run_id=latest.run_id
            )

            logger.info("Reloading from %s", latest_path)
            self.pipeline = joblib.load(latest_path)

            self.model_version = latest.version

            os.remove(latest_path)
        except mlflow.exceptions.MlflowException:
            logger.error(
                "Could not fetch version for model %s", self.model, exc_info=True
            )

    def predict(self, **kwargs) -> Union[float, bool, int]:
        if not self.initialized or self.pipeline is None:
            raise UninitializedPredictor("Predictor has not been initialized")
        X = pd.DataFrame(kwargs, index=[0])
        _f = (
            self.pipeline.predict_proba if self.probabilistic else self.pipeline.predict
        )
        return _f(X)[0]


ETAPredictor = MLFlowPredictor(FrameModels.ETA)
AvailabilityPredictor = MLFlowPredictor(FrameModels.AVAILABILITY, probabilistic=True)
