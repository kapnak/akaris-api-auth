import os
from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    f'.env.{os.getenv("ENV", "dev").lower()}' if 'ENV' in os.environ else '.env'
)

print(f'Using DOTENV: {DOTENV}')


class Config(BaseSettings):
    ENV: str
    DEBUG: bool = False
    PORT: int = 80
    JWT_PRIVATE_KEY_BASE64: str
    JWT_AUD: str
    JWT_EXPIRATION_HOURS: int
    LOG_LEVEL: str
    LOG_DIR: Optional[str] = None
    EIP_MESSAGE: str

    @field_validator('DEBUG', mode='before')
    @classmethod
    def empty_str_to_false(cls, v):
        if v == '':
            return False
        return v

    @field_validator('LOG_DIR', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == '':
            return None
        return v

    @field_validator('PORT', mode='before')
    @classmethod
    def empty_str_to_default(cls, v):
        if v == '':
            return 80
        return v

    @property
    def APP_NAME(self) -> str:
        return "auth-api"

    @property
    def APP_VERSION(self) -> str:
        version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'VERSION')
        try:
            with open(version_file, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            return "0.0.0"

    model_config = SettingsConfigDict(env_file=DOTENV)


config = Config()
