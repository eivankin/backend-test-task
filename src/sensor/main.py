import asyncio
import datetime as dt

import aiohttp
import aiohttp.client_exceptions

from common.configs import sensor, controller
from common.configs.logger import logging
from sensor.data_generator import sample_sensor
from common.messages.from_sensor import SensorMessage


async def send_data(data: SensorMessage):
    try:
        async with aiohttp.ClientSession(
            f"http://{controller.settings.HOST}:{controller.settings.PORT}"
        ) as session:
            async with session.post(
                f"{controller.settings.SENSOR_POST_ENDPOINT}",
                json=data,
            ) as response:
                if not response.ok:
                    logging.error(
                        f"Got error while sending request to the controller: "
                        f"{response.status} {response.reason}"
                    )

    except aiohttp.client_exceptions.ClientConnectionError as e:
        logging.error(
            f"Got error while sending request to the controller: "
            f"{e.__class__.__name__} {e}"
        )


async def assigner(
    messages_queue: asyncio.Queue,
    interval_secs: float = 1 / (sensor.settings.RPS * sensor.settings.RATE_MULTIPLIER),
    display_progress: bool = sensor.settings.DISPLAY_TQDM,
):
    progress = None
    if display_progress:
        try:
            from tqdm import tqdm
        except ImportError:
            display_progress = False
        else:
            progress = tqdm(mininterval=0.5)

    while True:
        if display_progress:
            progress.update()
            progress.set_description("\n")

        await messages_queue.put(
            SensorMessage(
                payload=int(sample_sensor()), datetime=dt.datetime.now()
            ).model_dump(mode="json")
        )
        await asyncio.sleep(interval_secs)


async def worker(messages_queue: asyncio.Queue):
    while True:
        task = await messages_queue.get()
        await send_data(task)


async def main(pool_size: int = sensor.settings.NUM_WORKERS):
    messages_queue = asyncio.Queue()
    workers = [asyncio.create_task(worker(messages_queue)) for _ in range(pool_size)]
    await asyncio.gather(assigner(messages_queue), *workers)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Sensor shutting down...")
