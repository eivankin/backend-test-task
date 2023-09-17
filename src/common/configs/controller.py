from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic.networks import MongoDsn


class ControllerSettings(BaseSettings):
    PORT: int = 8080
    HOST: str = "localhost"
    DECISION_INTERVAL_SECS: int = 5
    SENSOR_POST_ENDPOINT: str = "/sensor-data"
    MONGO_URL: MongoDsn = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "sus"
    NUM_WORKERS: int = 4

    model_config = SettingsConfigDict(env_prefix="CONTROLLER_")


settings = ControllerSettings()
