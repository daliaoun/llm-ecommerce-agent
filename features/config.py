import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load variables from root .env first, then features/.env as fallback.
_BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_BASE_DIR / ".env")
load_dotenv(Path(__file__).resolve().parent / ".env")


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    db_host: str = os.getenv("DB_HOST", "")
    db_user: str = os.getenv("DB_USER", "")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_name: str = os.getenv("DB_NAME", "")
    db_port: int = int(os.getenv("DB_PORT", "3306"))

    @property
    def db_config(self) -> dict:
        return {
            "host": self.db_host,
            "user": self.db_user,
            "password": self.db_password,
            "database": self.db_name,
            "port": self.db_port,
        }


settings = Settings()
