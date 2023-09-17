import asyncio
import datetime as dt
import math
import time

from scipy import stats

from common.configs import controller
from common.configs.logger import logging
from common.messages.from_controller import ManipulatorCommand
from controller.db import pop_last_mean, save_mean
from controller.db.decision_history_repo import DecisionHistoryRepo
from controller.db.sensor_data_repo import SensorDataRepo
from controller.socket_client import send_command_async

history_repo: DecisionHistoryRepo = DecisionHistoryRepo.create()
sensor_repo: SensorDataRepo = SensorDataRepo.create()


def t_test(
    hypothesis_mean: float,
    sample_size: int,
    sample_mean: float,
    sample_std: float,
    p_critical: float,
) -> bool:
    """Returns True if t-test rejects the null hypothesis."""
    t_statistic = (sample_mean - hypothesis_mean) / (
        sample_std / math.sqrt(sample_size)
    )
    p_value = 2 * (1 - stats.t.cdf(abs(t_statistic), sample_size - 1))
    return p_value < p_critical


async def make_decision(
    use_data_before: dt.datetime, p_critical: float = 0.05
) -> ManipulatorCommand:
    """
    Runs single mean t-test on sensor data with the previous mean as hypothesis.

    :param use_data_before: datetime of the end of the period to consider
    :param p_critical: p-value for t-test
    :return: manipulator command, keeps previous if t-test fails to reject the null hypothesis
    """
    hypothesis_mean = await pop_last_mean()
    delta = dt.timedelta(seconds=controller.settings.DECISION_INTERVAL_SECS)
    sample_size, sample_mean, sample_std = await sensor_repo.get_stats(
        use_data_before - delta,
        use_data_before,
    )
    await save_mean(sample_mean)
    await sensor_repo.delete_before(use_data_before)

    return await history_repo.update_history(
        use_data_before,
        not t_test(hypothesis_mean, sample_size, sample_mean, sample_std, p_critical),
    )


async def decision_loop():
    before_decision = time.time()
    before_decision_datetime = dt.datetime.now()
    await history_repo.update_history(before_decision_datetime, True)
    while True:
        await asyncio.sleep(
            controller.settings.DECISION_INTERVAL_SECS - (time.time() - before_decision)
        )
        before_decision = time.time()
        before_decision_datetime = dt.datetime.now()
        command = await make_decision(before_decision_datetime)
        try:
            await send_command_async(command, before_decision_datetime)
        except OSError as e:
            logging.error(f"Got error while sending manipulator command: {e}")
