from typing import Optional

import duckdb

from frame.config import cfg


def connect(
    s3_endpoint: str = None,
    s3_region: str = None,
    s3_access_key_id: str = None,
    s3_secret_access_key: str = None,
    memory_limit: Optional[int] = 4,
    threads: Optional[int] = 4,
    progress_bar: bool = True,
):
    cursor = duckdb.connect()
    if memory_limit is not None:
        cursor.execute(f"SET memory_limit='{memory_limit}GB'")

    if threads is not None:
        cursor.execute(f"SET threads TO {threads}")

    if progress_bar:
        cursor.execute("SET enable_progress_bar=true")

    cursor.execute("INSTALL httpfs;")
    cursor.execute("LOAD httpfs;")

    if s3_region is not None:
        cursor.execute(f"SET s3_region='{s3_region}'")

    cursor.execute(f"SET s3_endpoint='{s3_endpoint or cfg.s3.endpoint_url()}'")
    cursor.execute(f"SET s3_access_key_id='{s3_access_key_id or cfg.s3.access_key()}'")
    cursor.execute(
        f"SET s3_secret_access_key='{s3_secret_access_key or cfg.s3.secret_key()}'"
    )
    cursor.execute("SET s3_url_style='path'")
    cursor.execute("SET s3_use_ssl=true")

    return cursor
