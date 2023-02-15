from datetime import datetime
from io import BytesIO
import os
import tempfile

import duckdb
import joblib
import pandas as pd
import pyarrow.dataset as ds
from tqdm import tqdm

from frame.s3 import S3Client
from models.availability_model_trainer import FEATURES_ORDER, AvailabilityModelTrainer


def download_data(end_date: datetime, periods: int):
    s3_cli = S3Client()

    temp_dir = tempfile.TemporaryDirectory()

    dates = pd.date_range(end=end_date, periods=periods)
    for day in tqdm(dates):
        day_keys = s3_cli.client.Bucket("frame").objects.filter(Prefix=f"silver/status/year={day:%Y}/month={day:%m}/day={day:%-d}")
        for parquet_object in day_keys:
            parquet_temp_path = temp_dir.name + "/" + parquet_object.key
            os.makedirs(os.path.dirname(parquet_temp_path), exist_ok = True)
            s3_cli.client.Bucket("frame").download_file(Key=parquet_object.key, Filename=parquet_temp_path)

    dataset = ds.dataset(f"{temp_dir.name}/silver/status", format="parquet", partitioning="hive")
    con = duckdb.connect()
    con = con.register("status", dataset)

    return con

def train_availability(end_date: datetime):
    availability_model_trainer = AvailabilityModelTrainer()
    dataset_df = availability_model_trainer.create_dataset(end_date)
    availability_model_trainer.train_all_stations(dataset_df)
    availability_model_trainer.dump_stations_pipelines(end_date[-1], current=True)
