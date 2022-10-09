from typing import Optional

from pydantic import BaseModel


class Station(BaseModel):
    station_id: int
    name: str
    lat: float
    lon: float
    address: str
    capacity: int

    class Config:
        orm_mode = True


class StationStatus(BaseModel):
    station_id: int
    num_bikes_available: int
    num_bikes_disabled: int
    num_docks_available: int
    num_docks_disabled: int
    last_reported: Optional[int]

    class Config:
        orm_mode = True


class PredictionParams(BaseModel):
    user_eta: int
    user_lat: float
    user_lon: float


class Prediction(PredictionParams):
    station_id: int
    bike_availability_probability: float
    bike_eta: float

    class Config:
        orm_mode = True
