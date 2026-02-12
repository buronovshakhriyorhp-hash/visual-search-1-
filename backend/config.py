from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "Visual Similarity Search Engine"
    DEBUG: bool = False
    
    # ImgBB
    IMGBB_API_KEY: str
    
    # SerpApi
    SERPAPI_KEY: str
    
    # ML
    CONFIDENCE_THRESHOLD: float = 0.6
    INDEX_PATH: str = "data/deepfashion.index"
    METADATA_PATH: str = "data/metadata.json"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
