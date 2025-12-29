from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "RAM Companion API"
    ENV: str = "dev"

    # JWT
    JWT_SECRET: str = "change_me"
    JWT_ALGO: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MIN: int = 60

    # Database
    DATABASE_URL: str = "sqlite:///./ram_companion.db"

    # Destination provider
    DEST_PROVIDER: str = "mock"
    PLACES_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
