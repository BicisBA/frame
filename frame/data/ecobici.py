from functools import partial
from typing import Any, Dict, List, Literal, Optional

import requests
from pydantic import BaseModel

from frame.utils import get_logger
from frame.config import BA_BIKES_CREDS

logger = get_logger(__name__)

BASE_URL = partial(
    "https://apitransporte.buenosaires.gob.ar/ecobici/gbfs/{endpoint}?client_id={client_id}&client_secret={client_secret}".format,  # noqa: E501
    **BA_BIKES_CREDS
)

STATUS_ENDPOINT = "stationStatus"
STATIONS_ENDPOINT = "stationInformation"


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


def fetch_stations_status() -> List[EcobiciStationStatus]:
    logger.info("Fetching stations status from API")
    url = BASE_URL(endpoint=STATUS_ENDPOINT)
    response = requests.get(url, timeout=120)
    try:
        response.raise_for_status()
        return response.json()["data"]["stations"]
    except requests.exceptions.HTTPError:
        logger.error("Error fetching stations status from API", exc_info=True)
        raise


def fetch_stations_info() -> List[EcobiciStationInfo]:
    logger.info("Fetching stations information from API")
    url = BASE_URL(endpoint=STATIONS_ENDPOINT)
    response = requests.get(url, timeout=120)
    try:
        response.raise_for_status()
        return response.json()["data"]["stations"]
    except requests.exceptions.HTTPError:
        logger.error("Error fetching stations information from API", exc_info=True)
        raise
