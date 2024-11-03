
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["settings"]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    ) # type: ignore
    
    API_PORT: int = 8080
    LINKEDIN_EMAIL: str
    LINKEDIN_PASSWORD: str
    STYLE_CHOICE: str
    SEC_CH_UA: str
    SEC_CH_UA_PLATFORM: str
    USER_AGENT: str
    WEBHOOK_TOKEN: Optional[str] = None
    WEBHOOK_URI: Optional[str] = None
    BOT_ID: Optional[str] = None
    CHROME_PATH: str
    GOTENBERG_URL: str

settings = Settings()  # type: ignore
