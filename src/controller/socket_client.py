import asyncio
import datetime as dt

from common.configs import manipulator
from common.messages.from_controller import ControllerDecision, ManipulatorCommand


async def send_command_async(
    command: ManipulatorCommand, datetime: dt.datetime, encoding: str = "utf-8"
) -> None:
    payload = (
        ControllerDecision(datetime=datetime, status=command).model_dump_json() + "\n"
    )
    _, writer = await asyncio.open_connection(
        manipulator.settings.HOST, manipulator.settings.PORT
    )

    writer.write(payload.encode(encoding))
    await writer.drain()
    writer.close()
    await writer.wait_closed()
