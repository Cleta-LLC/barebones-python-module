"""Shared libraries used across services."""

from myapp.shared.config import DB_DIR, DEFAULT_DB_PATH, JSON_DIR, ROOT_DIR, ensure_data_dirs
from myapp.shared.logging import get_logger
from myapp.shared.schemas import BaseRecord, ServiceResponse

__all__ = [
    "BaseRecord",
    "DB_DIR",
    "DEFAULT_DB_PATH",
    "JSON_DIR",
    "ROOT_DIR",
    "ServiceResponse",
    "ensure_data_dirs",
    "get_logger",
]
