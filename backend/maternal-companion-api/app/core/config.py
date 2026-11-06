from functools import lru_cache
from typing import Literal

from cryptography.fernet import Fernet
from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Dev-only defaults so `uvicorn` works out of the box. Production refuses to start with them.
_DEV_JWT = "dev-only-jwt-secret"
_DEV_PEPPER = "dev-only-phone-pepper"
_DEV_FERNET = "DRP9v8RoAwRKgkggsRa0pBKI9S6ppNpr1AjyIQhn5Xo="
_PLACEHOLDERS = {"", "change-me", "change-me-too", "changeme", "secret"}
_MIN_SECRET_LENGTH = 32


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

    @field_validator("field_encryption_key")
    @classmethod
    def _valid_fernet_key(cls, value: SecretStr) -> SecretStr:
        try:
            Fernet(value.get_secret_value().encode())
        except (ValueError, TypeError) as exc:
            raise ValueError(
                "FIELD_ENCRYPTION_KEY is not a valid Fernet key. Either remove it from .env "
                "(local dev uses a built-in key) or generate one with: "
                'python -c "from cryptography.fernet import Fernet; '
                'print(Fernet.generate_key().decode())"'
            ) from exc
        return value

    @model_validator(mode="after")
    def _no_weak_secrets_outside_local(self) -> "Settings":
        if self.environment == "local":
            return self
        problems: list[str] = []
        for name, value, default in (
            ("JWT_SECRET", self.jwt_secret.get_secret_value(), _DEV_JWT),
            ("PHONE_HASH_PEPPER", self.phone_hash_pepper.get_secret_value(), _DEV_PEPPER),
        ):
            if value == default or value.lower() in _PLACEHOLDERS:
                problems.append(f"{name} is a dev/placeholder value")
            elif len(value) < _MIN_SECRET_LENGTH:
                problems.append(f"{name} must be at least {_MIN_SECRET_LENGTH} characters")
        if self.field_encryption_key.get_secret_value() == _DEV_FERNET:
            problems.append("FIELD_ENCRYPTION_KEY is the dev default")
        if problems:
            raise ValueError("Insecure configuration outside local: " + "; ".join(problems))
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
