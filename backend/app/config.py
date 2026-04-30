from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CROSSWALK_", env_file=".env", extra="ignore")

    data_dir: Path = Path("data")
    allowed_origins: list[str] = ["http://localhost:3000"]
    thumbnail_seconds: float = 1.0
    max_upload_mb: int = 200

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def outputs_dir(self) -> Path:
        return self.data_dir / "outputs"

    @property
    def samples_dir(self) -> Path:
        return self.data_dir / "samples"

    def ensure_dirs(self) -> None:
        for d in (self.uploads_dir, self.outputs_dir, self.samples_dir):
            d.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
