from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "My FastAPI App"
    environment: str = "development"
    database_url: str

    class Config:
        env_file = ".env"


settings = Settings()
