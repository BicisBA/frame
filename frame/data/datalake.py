from typing import Optional

import duckdb

from frame.config import cfg
from frame.utils import get_logger

logger = get_logger(__name__)


def connect(
    s3_endpoint: str = None,
    s3_region: str = None,
    s3_access_key_id: str = None,
    s3_secret_access_key: str = None,
    memory_limit: Optional[int] = cfg.duckdb.memory_limit(4, cast=int),
    threads: Optional[int] = cfg.duckdb.threads(4, cast=int),
    progress_bar: bool = cfg.duckdb.progress_bar(True, cast=bool),
):
    cursor = duckdb.connect()
    if memory_limit is not None:
        logger.info("Setting duckdb memory limit")
        cursor.execute(f"SET memory_limit='{memory_limit}GB'")

    if threads is not None:
        logger.info("Setting duckdb threads")
        cursor.execute(f"SET threads TO {threads}")

    if progress_bar:
        logger.info("Enabling progressbar")
        cursor.execute("SET enable_progress_bar=true")

    logger.info("Loading httpfs")
    cursor.execute("INSTALL httpfs;")
    cursor.execute("LOAD httpfs;")

    if s3_region is not None:
        logger.info("Setting s3 region")
        cursor.execute(f"SET s3_region='{s3_region}'")

    logger.info("Setting s3 endpoint")
    cursor.execute(f"SET s3_endpoint='{s3_endpoint or cfg.s3.endpoint_url()}'")

    logger.info("Setting s3 credentials")
    cursor.execute(f"SET s3_access_key_id='{s3_access_key_id or cfg.s3.access_key()}'")
    cursor.execute(
        f"SET s3_secret_access_key='{s3_secret_access_key or cfg.s3.secret_key()}'"
    )

    logger.info("Setting s3 url style")
    cursor.execute("SET s3_url_style='path'")

    logger.info("Enabling ssl")
    cursor.execute("SET s3_use_ssl=true")

    return cursor
