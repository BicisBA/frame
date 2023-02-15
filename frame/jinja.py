"""Jinja helpers."""
from typing import List
from uuid import uuid4

import jinja2
from jinjasql import JinjaSql
from pkg_resources import resource_filename
import sqlparse

from frame.utils import get_logger

logger = get_logger(__name__)


def wrap(iterable: List) -> List[str]:
    """Quote elements of list."""
    return [f"'{x}'" for x in iterable]


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
        trim_blocks=True, lstrip_blocks=True, undefined=jinja_logging_undef
    )
    env.filters["wrap"] = wrap

    if query_context_params:
        j = JinjaSql(env=env, param_style="pyformat")
        binded_sql, bind_params = j.prepare_query(sql, query_context_params)
        missing_placeholders = [
            k for k, v in bind_params.items() if jinja2.Undefined() == v
        ]

        assert (
            len(missing_placeholders) == 0
        ), f"Missing placeholders are: {missing_placeholders}"

        try:
            sql = binded_sql % bind_params
        except KeyError as exc:
            logger.error(exc)
            raise

    return sqlparse.format(sql, reindent=True, keyword_case="upper")
