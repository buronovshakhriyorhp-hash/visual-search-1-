from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "Visual Similarity Search Engine"
    DEBUG: bool = False
    
    IMGBB_API_KEY: str
    SERPAPI_KEY: str
    
    CONFIDENCE_THRESHOLD: float = 0.6
    INDEX_PATH: str = "data/deepfashion.index"
    METADATA_PATH: str = "data/metadata.json"

    class Config:
        env_file = ".env"
        extra = "ignore"
        env_file_encoding = 'utf-8'
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()
