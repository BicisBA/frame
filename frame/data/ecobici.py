from functools import partial

import requests

from frame.config import BA_BIKES_CREDS
from frame.utils import get_logger

logger = get_logger(__name__)

BASE_URL = partial(
    'https://apitransporte.buenosaires.gob.ar/ecobici/gbfs/{endpoint}?client_id={client_id}&client_secret={client_secret}'.format,  # noqa: E501
    **BA_BIKES_CREDS
)

STATUS_ENDPOINT = 'stationStatus'
STATIONS_ENDPOINT = 'stationInformation'


def fetch_stations():
    """Fetch stations from the ecobici API."""
    url = BASE_URL(endpoint=STATIONS_ENDPOINT)
    response = requests.get(url)
    if not response.ok:
        logger.error(response.status_code)
        raise Exception
    data = response.json()
    stations = data["data"]["stations"]
    return stations
