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
