from functools import lru_cache
from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Dev-only defaults so `uvicorn` works out of the box. Production refuses to start with them.
_DEV_JWT = "dev-only-jwt-secret"
_DEV_PEPPER = "dev-only-phone-pepper"
_DEV_FERNET = "DRP9v8RoAwRKgkggsRa0pBKI9S6ppNpr1AjyIQhn5Xo="


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Maternal Companion API"
    environment: Literal["local", "staging", "production"] = "local"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/maternal"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: SecretStr = SecretStr(_DEV_JWT)
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60

    # Phone numbers are stored encrypted (Fernet) and looked up via a keyed hash.
    field_encryption_key: SecretStr = SecretStr(_DEV_FERNET)
    phone_hash_pepper: SecretStr = SecretStr(_DEV_PEPPER)

    whatsapp_verify_token: SecretStr = SecretStr("dev-verify-token")
    whatsapp_app_secret: SecretStr = SecretStr("dev-app-secret")

    @model_validator(mode="after")
    def _no_dev_secrets_in_production(self) -> "Settings":
        if self.environment != "local":
            insecure = {
                "JWT_SECRET": self.jwt_secret.get_secret_value() == _DEV_JWT,
                "PHONE_HASH_PEPPER": self.phone_hash_pepper.get_secret_value() == _DEV_PEPPER,
                "FIELD_ENCRYPTION_KEY": self.field_encryption_key.get_secret_value() == _DEV_FERNET,
            }
            bad = [name for name, is_default in insecure.items() if is_default]
            if bad:
                raise ValueError(f"Dev default secrets not allowed outside local: {bad}")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
