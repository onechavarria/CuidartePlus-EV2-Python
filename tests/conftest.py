import sys
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def clean_modules(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test_secret_value_for_unit_tests")
    for key in list(sys.modules):
        if key == "app" or key.startswith("app."):
            del sys.modules[key]
    yield
    for key in list(sys.modules):
        if key == "app" or key.startswith("app."):
            del sys.modules[key]


@pytest.fixture
def load_service():
    def loader(name):
        root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(root / name))
        try:
            from app import main
            return main
        finally:
            sys.path.remove(str(root / name))
    return loader
