import datetime as dt
from collections import defaultdict

import pymongo
from bson import ObjectId

from common.configs import manipulator
from common.messages.from_controller import ManipulatorCommand
from controller.command_history import HistoryEntry
from controller.db import decision_history_collection
from controller.db.abstract_repo import AbstractRepo


class DecisionHistoryRepo(AbstractRepo):
    async def get_between(
        self, start: dt.datetime | None = None, end: dt.datetime | None = None
    ) -> list[HistoryEntry]:
        search_condition = defaultdict(dict)
        if start is not None:
            search_condition["from_datetime"]["$gte"] = start
        if end is not None:
            search_condition["to_datetime"]["$lte"] = end
        result = self._parse(
            await self._collection.find(dict(search_condition))
            .sort("to_datetime", pymongo.ASCENDING)
            .to_list(None)
        )
        if result and start is not None:
            result[0].from_datetime = start
        if result:
            result[-1].to_datetime = end if end is not None else dt.datetime.now()
        return result

    def _parse(self, raw_list: list[dict]) -> list[HistoryEntry]:
        return self._parse_as(raw_list, HistoryEntry)

    @classmethod
    def create(cls):
        return cls(decision_history_collection)

    async def get_previous_decision(self) -> tuple[ObjectId | None, ManipulatorCommand]:
        """
        :return: if there was no previous decisions and
        the previous decision if exists, default value otherwise
        """
        last_record = (
            await self._collection.find()
            .sort("from_datetime", pymongo.DESCENDING)
            .limit(1)
            .to_list(None)
        )
        last_decision = self._parse(last_record)

        if last_decision:
            return last_record[0]["_id"], last_decision[0].status
        return None, manipulator.settings.DEFAULT_STATE

    async def update_history(
        self, datetime: dt.datetime, keep_previous: bool
    ) -> ManipulatorCommand:
        obj_id, previous_decision = await self.get_previous_decision()
        if obj_id is None:
            obj_id = await self.save(
                HistoryEntry(
                    status=previous_decision,
                    from_datetime=datetime,
                    to_datetime=datetime,
                )
            )
        if keep_previous:
            return previous_decision

        new_command = (
            ManipulatorCommand.UP
            if previous_decision == ManipulatorCommand.DOWN
            else ManipulatorCommand.DOWN
        )
        await self._collection.update_one(
            {"_id": obj_id}, {"$set": {"to_datetime": datetime}}
        )
        await self.save(
            HistoryEntry(
                status=new_command, from_datetime=datetime, to_datetime=datetime
            )
        )

        return new_command
