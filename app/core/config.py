from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения.

    Значения читаются из переменных окружения и файла `.env`.

    Attributes:
        app_title: Название приложения для документации Swagger.
        app_description: Описание приложения для документации Swagger.
        app_version: Версия приложения.
        database_url: Адрес подключения к базе данных.
    """

    app_title: str = 'Благотворительный фонд поддержки котиков QRKot'
    app_description: str = 'Сервис для поддержки котиков'
    app_version: str = '0.1.0'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
