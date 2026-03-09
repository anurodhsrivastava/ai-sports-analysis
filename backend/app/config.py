"""Application configuration using pydantic-settings."""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    upload_dir: Path = Path("./uploads")
    results_dir: Path = Path("./results")
    task_store_dir: Path = Path("./task_store")
    models_dir: Path = Path("../models")
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"
    max_upload_size_mb: int = 500

    # Performance tuning
    inference_batch_size: int = 8
    inference_sample_rate: int = 6
    max_analysis_workers: int = 3
    cleanup_max_age_hours: int = 48

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]


settings = Settings()
