import pytest
from pydantic import ValidationError

from app.core.config import Settings

SECRET_VARS = ("JWT_SECRET", "PHONE_HASH_PEPPER", "FIELD_ENCRYPTION_KEY")
GOOD = {
    "jwt_secret": "x" * 40,
    "phone_hash_pepper": "y" * 40,
    "field_encryption_key": "Zm9vYmFyZm9vYmFyZm9vYmFyZm9vYmFyZm9vYmFyMTI=",
}


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Ignore the developer's shell and .env so these tests are deterministic."""
    for name in SECRET_VARS:
        monkeypatch.delenv(name, raising=False)


def make(**kwargs) -> Settings:
    return Settings(_env_file=None, **kwargs)


def test_local_works_with_built_in_dev_secrets():
    assert make(environment="local").environment == "local"


def test_production_refuses_dev_default_secrets():
    with pytest.raises(ValidationError):
        make(environment="production")


def test_production_refuses_placeholder_or_short_secrets():
    with pytest.raises(ValidationError):
        make(environment="production", **{**GOOD, "jwt_secret": "change-me"})
    with pytest.raises(ValidationError):
        make(environment="production", **{**GOOD, "phone_hash_pepper": "short"})


def test_production_accepts_real_secrets():
    assert make(environment="production", **GOOD).environment == "production"


def test_invalid_fernet_key_gives_a_clear_error():
    with pytest.raises(ValidationError, match="not a valid Fernet key"):
        make(environment="local", field_encryption_key="")
    with pytest.raises(ValidationError, match="not a valid Fernet key"):
        make(environment="local", field_encryption_key="not-a-key")
