"""Shared test fixtures available to all service tests."""

from pathlib import Path

import pytest


@pytest.fixture()
def data_dir(tmp_path: Path) -> Path:
    """Return a temporary data directory with json/ and db/ subdirs."""
    json_dir = tmp_path / "json"
    db_dir = tmp_path / "db"
    json_dir.mkdir()
    db_dir.mkdir()
    return tmp_path
