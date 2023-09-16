import datetime as dt
from enum import StrEnum

from pydantic import BaseModel


class ManipulatorCommand(StrEnum):
    UP = "up"
    DOWN = "down"


class ControllerDecision(BaseModel):
    datetime: dt.datetime
    status: ManipulatorCommand
