import datetime as dt

from pydantic import BaseModel


class SensorMessage(BaseModel):
    datetime: dt.datetime
    payload: int
