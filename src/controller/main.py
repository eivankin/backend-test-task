import asyncio
import datetime as dt
import logging
import time

from fastapi import FastAPI, HTTPException, status, Depends, BackgroundTasks
import uvicorn

from common.messages.from_controller import ManipulatorCommand
from controller.command_history import HistoryEntry
from common.messages.from_sensor import SensorMessage
from common.configs import controller
from controller.socket_client import send_command_async


app = FastAPI()
num_reqs = 0


def get_data_range(
    after: dt.datetime | None = None, before: dt.datetime | None = None
) -> tuple[dt.datetime | None, dt.datetime | None]:
    if (after is not None and before is not None) and after > before:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid datetime range"
        )
    return after, before


@app.post(controller.settings.SENSOR_POST_ENDPOINT)
async def post_data(data: SensorMessage) -> None:
    global num_reqs
    # TODO
    num_reqs += 1


@app.get("/history", response_model=list[HistoryEntry])
async def get_history(
    data_range: tuple[dt.datetime | None, dt.datetime | None] = Depends(get_data_range),
) -> list[HistoryEntry]:
    # TODO
    return []


async def decision_loop():
    while True:
        before_decision = time.time()
        command = (
            ManipulatorCommand.UP if num_reqs % 2 else ManipulatorCommand.DOWN
        )  # TODO
        try:
            await send_command_async(command)
        except OSError as e:
            logging.info(f"Got error while sending manipulator command: {e}")

        await asyncio.sleep(
            controller.settings.DECISION_INTERVAL_SECS - (time.time() - before_decision)
        )


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(decision_loop())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=controller.settings.PORT)
