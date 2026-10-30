from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    access_token_minutes: int = 30
    cookie_secure: bool = False  # True na VM, com HTTPS
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()