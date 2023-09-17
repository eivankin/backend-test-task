import pytest

from controller.db.decision_history_repo import DecisionHistoryRepo
from controller.db.sensor_data_repo import SensorDataRepo


@pytest.fixture
def history_repo(mocker):
    return mocker.MagicMock(spec=DecisionHistoryRepo)


@pytest.fixture
def sensor_repo(mocker):
    return mocker.MagicMock(spec=SensorDataRepo)


@pytest.fixture
def hypothesis_mean():
    return 10
