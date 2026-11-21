"""Tests for the platform server skeleton."""

from __future__ import annotations

import pytest
from app import __version__
from app.config import Settings, load_settings
from app.main import SIMULATION_NOTICE, create_app
from fastapi.testclient import TestClient


def client(**overrides) -> TestClient:
    settings = Settings(
        env="test", host="127.0.0.1", port=8000, cors_origins=("http://localhost:5173",), database_url=""
    )
    return TestClient(create_app(Settings(**{**settings.__dict__, **overrides})))


def test_health_reports_ok():
    response = client().get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_meta_exposes_version_environment_and_the_simulation_notice():
    body = client(env="test").get("/api/v1/meta").json()
    assert body["name"] == "PeregrinePulse"
    assert body["version"] == __version__
    assert body["environment"] == "test"
    assert body["simulation_notice"] == SIMULATION_NOTICE


def test_defaults_when_the_environment_is_empty():
    settings = load_settings({})
    assert (settings.env, settings.host, settings.port) == ("development", "127.0.0.1", 8000)
    assert settings.cors_origins == ("http://localhost:5173",)
    assert settings.database_url == ""


def test_environment_overrides_are_applied():
    settings = load_settings(
        {
            "PP_ENV": "production",
            "PP_API_HOST": "0.0.0.0",
            "PP_API_PORT": "9000",
            "PP_CORS_ORIGINS": "https://a.example, https://b.example",
            "PP_DATABASE_URL": "mysql://placeholder",
        }
    )
    assert settings.env == "production" and settings.port == 9000
    assert settings.cors_origins == ("https://a.example", "https://b.example")
    assert settings.database_url == "mysql://placeholder"


@pytest.mark.parametrize("value", ["abc", "0", "70000", ""])
def test_invalid_port_is_rejected(value):
    with pytest.raises(ValueError):
        load_settings({"PP_API_PORT": value})
