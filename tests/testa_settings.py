import pytest
from pydantic import ValidationError
from pydantic_settings import SettingsConfigDict

from settings import Settings


def testa_exemplo_valido():
    settings = Settings(DB_URL='sqlite+aiosqlite:///:memory:')
    assert settings.DB_URL == 'sqlite+aiosqlite:///:memory:'


def testa_exemplo_vazio():
    with pytest.raises(ValidationError):
        Settings(DB_URL='')


def testa_exemplo_unset(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv('DB_URL', raising=False)
    monkeypatch.setattr(
        Settings,
        'model_config',
        SettingsConfigDict(
            env_file_encoding='utf-8',
            case_sensitive=True,
            env_file=None,
        ),
    )
    with pytest.raises(ValidationError):
        Settings()


def testa_settings_carrega_db_url_do_env(monkeypatch: pytest.MonkeyPatch):
    # Simula variável de ambiente
    monkeypatch.setenv('DB_URL', 'sqlite+aiosqlite:///prod.db')

    settings = Settings()  # Carrega do .env
    assert settings.DB_URL == 'sqlite+aiosqlite:///prod.db'
