from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    access_token_minutes: int = 30
    cookie_secure: bool = False  # True na VM, com HTTPS
    api_rate_limit_user_per_minute: int = 100
    api_rate_limit_ip_per_minute: int = 300
    model_config = SettingsConfigDict(env_file=".env")

    @model_validator(mode="after")
    def _validar_configuracoes(self):
        if self.cookie_secure and len(self.secret_key) < 32:
            raise ValueError(
                "SECRET_KEY precisa ter 32+ caracteres quando COOKIE_SECURE=true. "
                'Gere uma com: python -c "import secrets; print(secrets.token_urlsafe(48))"'
            )
        if self.api_rate_limit_user_per_minute < 1:
            raise ValueError("API_RATE_LIMIT_USER_PER_MINUTE precisa ser maior que zero.")
        if self.api_rate_limit_ip_per_minute < 1:
            raise ValueError("API_RATE_LIMIT_IP_PER_MINUTE precisa ser maior que zero.")
        return self


settings = Settings()
