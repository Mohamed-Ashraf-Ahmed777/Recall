from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    app_name: str = "Recall"
    environment: str = "development"
    storage_originals_dir: Path = BASE_DIR / "storage" / "originals"
    storage_thumbnails_dir: Path = BASE_DIR / "storage" / "thumbnails"
    indexes_dir: Path = BASE_DIR / "indexes"
    database_url: str = f"sqlite:///{(BASE_DIR / "indexes" / "recall.db").as_posix()}"
    max_upload_size_bytes: int = 50 * 1024 * 1024

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")


settings = Settings()
