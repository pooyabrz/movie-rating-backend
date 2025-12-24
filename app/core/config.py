from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application Configuration
    """
    PROJECT_NAME: str = "Movie Rating System"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()
