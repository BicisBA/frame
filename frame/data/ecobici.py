import logging
from functools import partial
from typing import Any, Dict, List, Literal, Optional

import requests
import tenacity
from pydantic import BaseModel

from frame.utils import get_logger
from frame.config import BA_BIKES_CREDS
from frame.constants import ECOBICI_API, STATUS_ENDPOINT, STATIONS_ENDPOINT

logger = get_logger(__name__)

BASE_URL = partial(ECOBICI_API.format, **BA_BIKES_CREDS)  # noqa: E501


class EcobiciStationStatus(BaseModel):
    is_charging_station: bool
    is_installed: Literal[0, 1]
    is_renting: Literal[0, 1]
    is_returning: Literal[0, 1]
    last_reported: int
    num_bikes_available: int
    num_bikes_disabled: int
    num_bikes_available_types: Dict[Literal["ebike", "mechanical"], int]
    num_docks_available: int
    num_docks_disabled: int
    station_id: str
    status: Literal["IN_SERVICE", "END_OF_LIFE"]
    traffic: Optional[Any]


class EcobiciStationInfo(BaseModel):
    _ride_code_support: bool
    address: str
    altitude: float
    capacity: int
    groups: List[str]
    is_charging_station: bool
    lat: float
    lon: float
    name: str
    nearby_distance: float
    obcn: str
    physical_configuration: str
    post_code: str
    rental_mehtods: List[str]
    station_id: str


@tenacity.retry(
    wait=tenacity.wait_fixed(30),
    retry=tenacity.retry_if_exception_type(requests.exceptions.HTTPError),
    stop=tenacity.stop_after_attempt(30),
    before=tenacity.before_log(logger, logging.INFO),
)
def fetch_stations_status() -> List[EcobiciStationStatus]:
    """Fetch stations' status from the EcoBici API."""
    logger.info("Fetching stations status from API")
    url = BASE_URL(endpoint=STATUS_ENDPOINT)
    response = requests.get(url, timeout=120)
    try:
        response.raise_for_status()
        stations_status = response.json()["data"]["stations"]
        for station_status in stations_status:
            station_status["station_id"] = int(station_status["station_id"])
        return stations_status
    except requests.exceptions.HTTPError:
        logger.error("Error fetching stations status from API", exc_info=True)
        raise


@tenacity.retry(
    wait=tenacity.wait_fixed(30),
    retry=tenacity.retry_if_exception_type(requests.exceptions.HTTPError),
    stop=tenacity.stop_after_attempt(30),
    before=tenacity.before_log(logger, logging.INFO),
)
def fetch_stations_info() -> List[EcobiciStationInfo]:
    """Fetch information on all stations from the EcoBici API."""
    logger.info("Fetching stations information from API")
    url = BASE_URL(endpoint=STATIONS_ENDPOINT)
    response = requests.get(url, timeout=120)
    try:
        response.raise_for_status()
        stations_info = response.json()["data"]["stations"]
        for station_info in stations_info:
            station_info["station_id"] = int(station_info["station_id"])
        return stations_info
    except requests.exceptions.HTTPError:
        logger.error("Error fetching stations information from API", exc_info=True)
        raise
