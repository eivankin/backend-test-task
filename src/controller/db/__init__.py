import logging

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

from common.configs.controller import settings


client = AsyncIOMotorClient(str(settings.MONGO_URL))
database: AsyncIOMotorDatabase = client.get_database(settings.MONGO_DB_NAME)
sensor_data_collection: AsyncIOMotorCollection = database.get_collection("sensor_data")
decision_history_collection: AsyncIOMotorCollection = database.get_collection(
    "decision_history"
)
mean_collection: AsyncIOMotorCollection = database.get_collection("mean")


async def pop_last_mean(default_value: float = 0) -> float:
    last_mean = await mean_collection.find_one()
    if last_mean:
        await mean_collection.delete_many({})
        return last_mean["mean"]
    return default_value


async def save_mean(mean: float) -> None:
    await mean_collection.insert_one({"mean": mean})
