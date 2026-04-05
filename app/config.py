from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Finance Dashboard API"
    SECRET_KEY: str = "supersecretkey-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    DATABASE_URL: str = "sqlite:///./finance.db"

    class Config:
        env_file = ".env"


settings = Settings()
