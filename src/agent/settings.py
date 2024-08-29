from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class RetellSettings(BaseModel):
    api_key: str = ""
    agent_id: str = ""


class TwilioSettings(BaseModel):
    account_id: str = ""
    auth_token: str = ""
    phone_number: str = ""

    key: str = ""
    api_secret: str = ""
    account_sid: str = ""


class NGrokSettings(BaseModel):
    ip_address: str = ""


class FastAPISettings(BaseModel):
    port: int = 8000
    reload: bool = False


class Settings(BaseSettings):
    retell: RetellSettings = RetellSettings()
    twilio: TwilioSettings = TwilioSettings()
    ngrok: NGrokSettings = NGrokSettings()
    fastapi: FastAPISettings = FastAPISettings()

    model_config = SettingsConfigDict(
        env_nested_delimiter="__", env_file=".env", extra="ignore"
    )


settings = Settings()
