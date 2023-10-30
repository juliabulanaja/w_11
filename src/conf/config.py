from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError

import os


class Settings(BaseSettings):
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: str
    mail_server: str
    sqlalchemy_database_url: str
    secret_key: str
    algorithm: str
    redis_host: str
    redis_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_port: int = 5432
    postgres_host: str
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    # model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    model_config = SettingsConfigDict(env_file=f"{os.path.dirname(os.path.abspath(__file__))}/../../.env", env_file_encoding="utf-8")

try:
    settings = Settings()
except ValidationError as exc:
    # print(repr(exc.errors()[0]['type']))
    print(exc)

