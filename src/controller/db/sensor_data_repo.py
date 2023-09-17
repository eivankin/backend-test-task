import datetime as dt
from collections import defaultdict

from motor.motor_asyncio import AsyncIOMotorCursor

from common.configs.logger import logging
from common.messages.from_sensor import SensorMessage
from controller.db import sensor_data_collection
from controller.db.abstract_repo import AbstractRepo


class SensorDataRepo(AbstractRepo):
    @classmethod
    def create(cls):
        return cls(sensor_data_collection)

    async def get_between(
        self, start: dt.datetime | None = None, end: dt.datetime | None = None
    ) -> list[SensorMessage]:
        return self._parse(await self._get_cursor_between(start, end).to_list(None))

    async def _get_cursor_between(
        self, start: dt.datetime | None = None, end: dt.datetime | None = None
    ) -> AsyncIOMotorCursor:
        return await self._collection.find(self._get_search_condition(start, end))

    @staticmethod
    def _get_search_condition(
        start: dt.datetime | None = None, end: dt.datetime | None = None
    ) -> dict:
        search_condition = defaultdict(dict)
        if start is not None:
            search_condition["datetime"]["$gte"] = start
        if end is not None:
            search_condition["datetime"]["$lte"] = end
        return dict(search_condition)

    async def get_stats(
        self, start: dt.datetime | None = None, end: dt.datetime | None = None
    ) -> tuple[int, float, float]:
        """
        Calculates sample mean and standard deviation for sensor data in given period.

        :param start: start of the period
        :param end: end of the period
        :return: tuple of number of records, mean and standard deviation
        """
        pipeline = [
            {"$match": self._get_search_condition(start, end)},
            {
                "$group": {
                    "_id": None,
                    "count": {"$sum": 1},
                    "mean": {"$avg": "$payload"},
                    "std": {"$stdDevSamp": "$payload"},
                },
            },
        ]
        try:
            result, *_ = await self._collection.aggregate(pipeline).to_list(None)
        except ValueError:
            logging.error(
                "Got error while calculating statistics, returning default value"
            )
            return 1, 0, 1
        return result["count"], result["mean"], result["std"]

    async def delete_before(self, before: dt.datetime) -> None:
        await self._collection.delete_many({"datetime": {"$lte": before}})

    def _parse(self, raw_list: list[dict]) -> list[SensorMessage]:
        return self._parse_as(raw_list, SensorMessage)
