from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    app_name: str = "Neural Remix Engine"
    upload_dir: Path = Path("uploads")
    output_dir: Path = Path("outputs")
    cache_dir: Path = Path("cache")
    
    redis_host: str = "localhost"
    redis_port: int = 6379
    
    max_file_size: int = 100 * 1024 * 1024
    allowed_formats: list[str] = [".mp3", ".wav", ".flac", ".m4a"]
    
    demucs_model: str = "htdemucs"
    musicgen_model: str = "facebook/musicgen-melody"
    
    class Config:
        env_file = ".env"

settings = Settings()

settings.upload_dir.mkdir(exist_ok=True)
settings.output_dir.mkdir(exist_ok=True)
settings.cache_dir.mkdir(exist_ok=True)

