from datetime import datetime

from pydantic import BaseModel


class Station(BaseModel):
    id: int
    name: str
    lat: float
    lon: float
    address: str
    capacity: int

    class Config:
        orm_mode = True
