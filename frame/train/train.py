import os
import time
import operator as ops
from datetime import datetime, timedelta
from typing import Tuple, Union, Callable, Optional

import duckdb
import joblib
import mlflow
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator
from mlflow.tracking import MlflowClient
from sklearn.model_selection import train_test_split

from frame.config import cfg
from frame.data.datalake import connect
from frame.utils import with_env, get_logger
from frame import __version__ as frame_version
from frame.jinja import load_sql_query, render_sql_query
from frame.constants import MODELS_QUERIES, DEFAULT_TEST_SIZE, FrameModels, MLFlowStage

logger = get_logger(__name__)


@with_env(
    MLFLOW_TRACKING_USERNAME=cfg.mlflow.username(),
    MLFLOW_TRACKING_PASSWORD=cfg.mlflow.password(),
    MLFLOW_TRACKING_SERVER_CERT_PATH=cfg.mlflow.cert_path(),
)
def train_model(
    model: FrameModels,
    estimator: Union[Pipeline, BaseEstimator],
    num_features: Tuple[str, ...],
    cat_features: Tuple[str, ...],
    target: str,
    mlflow_tracking_uri=cfg.mlflow.uri(),
    con: Optional[duckdb.DuckDBPyConnection] = None,
    test_size: float = DEFAULT_TEST_SIZE,
    metrics: Optional[Tuple[Callable]] = None,
    query: Optional[str] = None,
    **query_kws,
):
    con = con if con is not None else connect()
    if query is None:
        sql = load_sql_query(MODELS_QUERIES[model])
        rendered_query = render_sql_query(sql, **query_kws)

    logger.info("Executing query")
    t0 = time.time()
    dataset = con.execute(rendered_query).df().dropna()
    t1 = time.time()
    logger.info("Query finished in %s", timedelta(seconds=t1 - t0))
    logger.info("Total dataset size %s", len(dataset))

    mlflow_client = MlflowClient(mlflow_tracking_uri)

    run_date = datetime.now()

    experiment_name = f"prod_{model}"
    run_name = f"{experiment_name}_{run_date}"

    try:
        logger.info("Trying to fetch latest version for model %s", model)
        versions = mlflow_client.get_latest_versions(model)
        if versions:
            latest = max(versions, key=ops.attrgetter("creation_timestamp"))
            logger.info("Latest version for model %s was %s", model, latest)
    except mlflow.exceptions.RestException:
        logger.info(
            "No previous versions found for model %s. Registering first version.", model
        )
        mlflow_client.create_registered_model(model)

    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(experiment_name)
    with mlflow.start_run(run_name=run_name) as run:
        mlflow.log_param("frame_version", frame_version)
        mlflow.log_param("num_features", num_features)
        mlflow.log_param("cat_features", cat_features)
        mlflow.log_param("query_bindings", query_kws)

        X_train, X_test, y_train, y_test = train_test_split(
            dataset.drop(columns=[target]),
            dataset[target],
            test_size=test_size,
            shuffle=False,
        )

        logger.info("Fitting estimator")
        estimator.fit(X_train, y_train)

        logger.info("Logging metrics")
        if metrics is not None:
            preds = estimator.predict(X_test)
            for metric in metrics:
                mlflow.log_metric(metric.__name__, metric(y_test, preds))

        mlflow.log_metric("train_samples", len(X_train))
        mlflow.log_metric("test_samples", len(X_test))

        estimator_path = f"{model}.joblib"

        logger.info("Dumping estimator")
        joblib.dump(estimator, estimator_path)
        mlflow.log_artifact(estimator_path)

        new_version = mlflow_client.create_model_version(
            model, estimator_path, run.info.run_id
        )
        mlflow_client.transition_model_version_stage(
            model, new_version.version, MLFlowStage.Production.value
        )

        os.remove(estimator_path)
