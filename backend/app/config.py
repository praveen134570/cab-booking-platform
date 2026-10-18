from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://cab_user:cab_password@localhost:5432/cab_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    STRIPE_SECRET_KEY: str = "sk_test_placeholder"
    STRIPE_WEBHOOK_SECRET: str = "whsec_placeholder"
    GOOGLE_MAPS_API_KEY: str = "google_key_placeholder"
    CLERK_PEM_PUBLIC_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
