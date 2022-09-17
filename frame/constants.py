"""Useful constants to use throughout frame and beyond."""

import enum
import pathlib

DEFAULT_SQLITE_LOC = pathlib.Path(__name__).parent.parent / "frame.db"
DEFAULT_SQLITE = f"sqlite:////{DEFAULT_SQLITE_LOC.resolve()}"
DEFAULT_API_SECRET = "wH*0#m$l`4v7e'HF;Hez'6fhNuthKH`Eg|#[<5FILs19}<P@"


class Environments(enum.Enum):
    DEV = "dev"
    PROD = "prod"
    TEST = "test"
