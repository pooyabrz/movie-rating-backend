from typing import Optional
import os
from dotenv import load_dotenv

class Settings:
    """
    Application Configuration
    """
    def __init__(self, env_file: str = ".env"):
        # Load environment variables from .env file
        load_dotenv(env_file)
        
        self.PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Movie Rating System")
        self.API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "")
        
        # Logging configuration
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
        self.SERVICE_NAME: str = os.getenv("SERVICE_NAME", "movie-rating-api")
        
        # Validate required fields
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL must be set in environment or .env file")

settings = Settings()