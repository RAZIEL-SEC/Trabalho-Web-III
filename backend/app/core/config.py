from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    access_token_minutes: int = 30
    cookie_secure: bool = False  # True na VM, com HTTPS
    model_config = SettingsConfigDict(env_file=".env")

    @model_validator(mode="after")
    def _exigir_chave_forte_com_https(self):
        if self.cookie_secure and len(self.secret_key) < 32:
            raise ValueError(
                "SECRET_KEY precisa ter 32+ caracteres quando COOKIE_SECURE=true. "
                'Gere uma com: python -c "import secrets; print(secrets.token_urlsafe(48))"'
            )
        return self


settings = Settings()
