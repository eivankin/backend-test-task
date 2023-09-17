from random import normalvariate, seed

from common.configs.sensor import settings

seed(settings.SEED)


def sample_sensor() -> float:
    return normalvariate(settings.MEAN, settings.STD)
