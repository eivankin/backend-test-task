from abc import ABC, abstractmethod
import datetime as dt
from typing import TypeVar

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel, TypeAdapter


T = TypeVar("T", bound=BaseModel)


class AbstractRepo(ABC):
    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self._collection = collection

    async def save(self, data: BaseModel) -> ObjectId:
        return (await self._collection.insert_one(data.model_dump())).inserted_id

    @abstractmethod
    async def get_between(
        self, start: dt.datetime | None = None, end: dt.datetime | None = None
    ) -> list[T]:
        ...

    @staticmethod
    def _parse_as(raw_list: list[dict], target_model: type[T]) -> list[T]:
        return TypeAdapter(list[target_model]).validate_python(raw_list)

    @abstractmethod
    def _parse(self, raw_list: list[dict]) -> list[T]:
        ...
