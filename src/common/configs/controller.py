from pydantic_settings import BaseSettings, SettingsConfigDict


class ControllerSettings(BaseSettings):
    PORT: int = 8080
    HOST: str = "localhost"
    DECISION_INTERVAL_SECS: int = 5
    SENSOR_POST_ENDPOINT: str = "/sensor-data"

    model_config = SettingsConfigDict(env_prefix="CONTROLLER_")


settings = ControllerSettings()
