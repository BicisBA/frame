"""Endpoints dependencies."""
import os
import operator as ops
from typing import List, Optional

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
    def __init__(self, model: FrameModels, tracking_uri: str = cfg.mlflow.uri()):
        self.model = model
        self.tracking_uri = tracking_uri
        self.pipeline: Optional[Pipeline] = None
        self.model_version: Optional[int] = None
        self.initialized = False

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

            if self.model_version is not None and self.model_version == latest:
                logger.info("Already at latest model for %s", self.model)
                return

            latest_path = mlflow.artifacts.download_artifacts(
                artifact_path=f"{self.model}.joblib", run_id=latest.run_id
            )
            self.pipeline = joblib.load(latest_path)

            os.remove(latest_path)
            self.initialized = True
        except mlflow.exceptions.MlflowException:
            logger.error(
                "Could not fetch version for model %s", self.model, exc_info=True
            )

    def predict(self, **kwargs):
        if not self.initialized:
            raise UninitializedPredictor("Predictor has not been initialized")
        X = pd.DataFrame(kwargs, index=[0])
        return self.pipeline.predict(X)


ETAPredictor = MLFlowPredictor(FrameModels.ETA)
AvailabilityPredictor = MLFlowPredictor(FrameModels.AVAILABILITY)
