import datetime as dt

from pydantic import BaseModel

from common.messages.from_controller import ManipulatorCommand


class HistoryEntry(BaseModel):
    from_datetime: dt.datetime
    to_datetime: dt.datetime
    status: ManipulatorCommand
