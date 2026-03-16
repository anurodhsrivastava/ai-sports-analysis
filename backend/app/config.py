"""Application configuration using pydantic-settings."""

import os
from pathlib import Path

from pydantic_settings import BaseSettings

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


class Settings(BaseSettings):
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    upload_dir: Path = Path("./uploads")
    results_dir: Path = Path("./results")
    task_store_dir: Path = Path("./task_store")
    wishlist_dir: Path = Path("./wishlist")
    models_dir: Path = Path("../models")
    model_path: Path = Path("../models/snowboard_pose_model.pt")
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"
    max_upload_size_mb: int = 500

    # OAuth settings (stubs for integration)
    google_client_id: str = ""
    google_client_secret: str = ""
    facebook_app_id: str = ""
    facebook_app_secret: str = ""
    jwt_secret: str = "change-me-in-production"
    environment: str = "development"

    # Database
    database_url: str = "sqlite:///./app.db"

    # Payment (Stripe)
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id_pro: str = ""

    # Tier limits
    free_tier_videos_per_sport: int = 1
    pro_tier_videos_per_sport: int = 50

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
