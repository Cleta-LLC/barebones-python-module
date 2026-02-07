"""Application-wide configuration."""

from pathlib import Path

# Repository root (two levels up from src/myapp/)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent

DATA_DIR = ROOT_DIR / "data"
JSON_DIR = DATA_DIR / "json"
DB_DIR = DATA_DIR / "db"
DEFAULT_DB_PATH = DB_DIR / "myapp.db"


def ensure_data_dirs() -> None:
    """Create data directories if they do not exist."""
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    DB_DIR.mkdir(parents=True, exist_ok=True)
