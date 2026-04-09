import os
from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    f'.env.{os.getenv('ENV', 'dev').lower()}' if 'ENV' in os.environ else '.env'
)

print(f'Using DOTENV: {DOTENV}')


class Config(BaseSettings):
    ENV: str
    DEBUG: bool
    PORT: int
    JWT_PRIVATE_KEY_BASE64: str
    JWT_AUD: str
    JWT_EXPIRATION_HOURS: int
    APP_NAME: str
    APP_VERSION: str
    LOG_LEVEL: str
    LOG_DIR: str
    EIP_MESSAGE: str

    model_config = SettingsConfigDict(env_file=DOTENV)


config = Config()
