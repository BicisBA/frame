"""Jinja helpers."""
from typing import List, Optional

import jinja2
import sqlparse
from jinjasql import JinjaSql
from pkg_resources import resource_filename

from frame.config import cfg
from frame.utils import get_logger

logger = get_logger(__name__)


def wrap(iterable: List) -> List[str]:
    """Quote elements of list."""
    return [f"'{x}'" for x in iterable]


def parquet_partitioned_table(
    table: str = "status",
    bucket: str = cfg.s3.bucket(),
    level: str = "silver",
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
    hour: Optional[int] = None,
) -> str:
    year_str: str = f"/year={year if year is not None else '*'}"
    month_str: str = f"/month={month if month is not None else '*'}"
    day_str: str = f"/day={day if day is not None else '*'}"
    hour_str: str = f"/hour={hour if hour is not None else '*'}"
    return f"parquet_scan('s3://{bucket}/{level}/{table}{year_str}{month_str}{day_str}{hour_str}/*.parquet', HIVE_PARTITIONING=1)"


def load_sql_query(filename: str) -> str:
    """Load a SQL query from package resources.

    Parameters
    ----------
    filename: Filename to load


    Returns
    -------
    Raw query SQL.
    """
    logger.info("Loading query from %s", filename)
    with open(  # pylint: disable=unspecified-encoding
        resource_filename("frame", f"resources/sql/{filename}.sql")
    ) as query_template_file:
        return query_template_file.read()


def render_sql_query(sql: str, **query_context_params) -> str:
    """Render jinja sql with params.
    Parameters
    ----------
    sql : str
        Query to be formatted.
    query_context_params : Any
        Parameters to format the query.
    Returns
    -------
    sql : str
        Formatted query.
    """
    jinja_logging_undef = jinja2.make_logging_undefined(
        logger=logger, base=jinja2.Undefined
    )
    env = jinja2.Environment(
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=jinja_logging_undef,
        autoescape=True,
    )
    env.filters["wrap"] = wrap
    env.globals.update(
        dict(
            parquet_partitioned_table=parquet_partitioned_table,
        )
    )

    j = JinjaSql(env=env, param_style="pyformat")
    binded_sql, bind_params = j.prepare_query(sql, query_context_params)
    missing_placeholders = [
        k for k, v in bind_params.items() if jinja2.Undefined() == v
    ]

    if len(missing_placeholders) > 0:
        raise ValueError(f"Missing placeholders are: {missing_placeholders}")

    try:
        sql = binded_sql % bind_params
    except KeyError as exc:
        logger.error(exc)
        raise

    return sqlparse.format(sql, reindent=True, keyword_case="upper")
