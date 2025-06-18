import logging
import sys

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pythonjsonlogger.json import JsonFormatter


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
    )
    DB_URL: str = Field(default='', min_length=1)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    SECRET_KEY: str = Field(default='')
    ALGORITHM: str = Field(default='')
    GRAFANA_PASSWORD: str = Field(default='')
    LOG_LEVEL: str = 'info'
    SERVICE_NAME: str = 'auth-service'
    ENVIRONMENT: str = 'development'


settings = Settings()


class CustomJsonFormatter(JsonFormatter):
    """Formata logs para JSON com campos personalizados"""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['service'] = settings.SERVICE_NAME
        log_record['environment'] = settings.ENVIRONMENT
        log_record['logger'] = record.name


def setup_logger():
    """Configura o logger raiz da aplicação"""
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL.upper())

    # Remove handlers existentes (evita duplicação)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Handler para stdout (Docker/Promtail)
    stream_handler = logging.StreamHandler(sys.stdout)

    # Formatação JSON
    formatter = CustomJsonFormatter(
        '%(asctime)s %(levelname)s %(message)s %(logger)s %(service)s %(environment)s'
    )
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    return logger
