from typing import Tuple

import youconfigme as ycm

from frame.constants import (
    JOBLIB_COMPRESSION_LEVEL,
    JOBLIB_COMPRESSION_ALGORITHM,
    Environments,
)

cfg = ycm.AutoConfig()

env = cfg.env(default=Environments.DEV.value)

JOBLIB_COMPRESSION: Tuple[str, int] = (
    cfg.models.compression_algorithm(default=JOBLIB_COMPRESSION_ALGORITHM),
    cfg.models.compression_level(default=JOBLIB_COMPRESSION_LEVEL, cast=int),
)

BA_BIKES_CREDS = {
    "client_id": cfg.ecobici.client_id(),
    "client_secret": cfg.ecobici.client_secret(),
}
