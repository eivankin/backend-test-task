import asyncio
import datetime as dt
import subprocess

from fastapi import FastAPI, HTTPException, status, Depends

from controller.command_history import HistoryEntry
from common.messages.from_sensor import SensorMessage
from common.configs.controller import settings
from controller.db.decision_history_repo import DecisionHistoryRepo
from common.configs.logger import logging
from controller.db.sensor_data_repo import SensorDataRepo
from controller.make_decision import decision_loop

app = FastAPI()
reqs = 0


async def count_rps():
    global reqs
    while True:
        logging.error(
            f"RPS per worker: {reqs}, total (predicted): {reqs * settings.NUM_WORKERS}"
        )
        reqs = 0
        await asyncio.sleep(1)


def get_data_range(
    after: dt.datetime | None = None, before: dt.datetime | None = None
) -> tuple[dt.datetime | None, dt.datetime | None]:
    if (after is not None and before is not None) and after > before:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid datetime range"
        )
    return after, before


@app.post(settings.SENSOR_POST_ENDPOINT)
async def post_data(
    data: SensorMessage, repository: SensorDataRepo = Depends(SensorDataRepo.create)
) -> None:
    global reqs
    reqs += 1
    await repository.save(data)


@app.get("/history", response_model=list[HistoryEntry])
async def get_history(
    data_range: tuple[dt.datetime | None, dt.datetime | None] = Depends(get_data_range),
    repository: DecisionHistoryRepo = Depends(DecisionHistoryRepo.create),
) -> list[HistoryEntry]:
    return await repository.get_between(*data_range)


@app.on_event("startup")
async def startup_event():
    # asyncio.create_task(decision_loop())
    asyncio.create_task(count_rps())


if __name__ == "__main__":
    # This seems like bad practice, but it works, so I am happy
    proc = subprocess.Popen(
        [
            "gunicorn",
            "controller.main:app",
            "--workers",
            str(settings.NUM_WORKERS),
            "--worker-class",
            "uvicorn.workers.UvicornWorker",
            "--bind",
            f"0.0.0.0:{settings.PORT}",
        ]
    )
    asyncio.run(decision_loop())
    proc.kill()
