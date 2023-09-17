import pytest
import datetime as dt

from common.configs.manipulator import settings as manipulator_settings


@pytest.fixture
def use_data_before():
    return dt.datetime.now()


@pytest.fixture
def make_decision(mocker, hypothesis_mean):
    mocker.patch("controller.decision.save_mean")
    mocker.patch("controller.decision.pop_last_mean", return_value=hypothesis_mean)

    import controller.decision

    return controller.decision.make_decision


@pytest.mark.asyncio
async def test_make_decision_change_status(
    history_repo,
    sensor_repo,
    use_data_before,
    make_decision,
):
    sample_size = 100
    sample_mean = 12
    sample_std = 2
    sensor_repo.get_stats.return_value = (sample_size, sample_mean, sample_std)

    result = await make_decision(use_data_before, history_repo, sensor_repo)

    assert result != manipulator_settings.DEFAULT_STATE  # Check if status changed
    history_repo.update_history.assert_called_with(
        use_data_before, False
    )  # Check if 'update_history is called with correct args


@pytest.mark.asyncio
async def test_make_decision_keep_status(
    history_repo, sensor_repo, use_data_before, make_decision, hypothesis_mean
):
    sample_size = 100
    sample_mean = hypothesis_mean
    sample_std = 2
    sensor_repo.get_stats.return_value = (sample_size, sample_mean, sample_std)

    result = await make_decision(use_data_before, history_repo, sensor_repo)

    assert result != manipulator_settings.DEFAULT_STATE  # Check if status changed
    history_repo.update_history.assert_called_with(
        use_data_before, True
    )  # Check if 'update_history is called with correct args
