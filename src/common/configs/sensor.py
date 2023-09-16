from pydantic_settings import BaseSettings, SettingsConfigDict


class SensorSettings(BaseSettings):
    """
    Settings for the sensor.

    Attributes:
        RPS (int): Requests per second.
        MEAN (float): Normal distribution parameter (mu for normalvariate).
        STD (float): Normal distribution parameter (sigma for normalvariate).
        SEED (int): Random generation seed for reproducibility.
        NUM_WORKERS (int): Number of workers in asyncio pool to make requests.
        DISPLAY_TQDM (bool): Whether to display the progress bar with request rate.
        RATE_MULTIPLIER (float): Manually tuned constant to achieve given RPS.
        model_config (SettingsConfigDict): Configuration for the sensor model.
    """

    RPS: int = 300
    MEAN: float = 0.0
    STD: float = 10
    SEED: int = 42
    NUM_WORKERS: int = 16
    DISPLAY_TQDM: bool = True
    RATE_MULTIPLIER: float = 1.25

    model_config = SettingsConfigDict(env_prefix="SENSOR_")


settings = SensorSettings()
