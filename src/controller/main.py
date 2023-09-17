import asyncio
import datetime as dt
import subprocess

from fastapi import Depends, FastAPI, HTTPException, status

from common.configs.controller import settings
from common.messages.from_sensor import SensorMessage
from controller.command_history import HistoryEntry
from controller.db.decision_history_repo import DecisionHistoryRepo
from controller.db.sensor_data_repo import SensorDataRepo
from controller.decision import decision_loop

app = FastAPI()


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
    await repository.save(data)


@app.get("/history", response_model=list[HistoryEntry])
async def get_history(
    data_range: tuple[dt.datetime | None, dt.datetime | None] = Depends(get_data_range),
    repository: DecisionHistoryRepo = Depends(DecisionHistoryRepo.create),
) -> list[HistoryEntry]:
    return await repository.get_between(*data_range)


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
