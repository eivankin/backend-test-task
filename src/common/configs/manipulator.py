from pydantic_settings import BaseSettings, SettingsConfigDict


from common.messages.from_controller import ManipulatorCommand


class ManipulatorSettings(BaseSettings):
    PORT: int = 1234
    HOST: str = "localhost"
    DEFAULT_STATE: ManipulatorCommand = ManipulatorCommand.DOWN

    model_config = SettingsConfigDict(env_prefix="MANIPULATOR_")


settings = ManipulatorSettings()
