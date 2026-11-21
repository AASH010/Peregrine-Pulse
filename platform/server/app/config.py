"""Settings read from the process environment. See .env.example for the variable names."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    env: str
    host: str
    port: int
    cors_origins: tuple[str, ...]
    database_url: str


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    """Build settings from the environment; invalid values raise ValueError."""
    source = os.environ if environ is None else environ
    port_text = source.get("PP_API_PORT", "8000")
    try:
        port = int(port_text)
    except ValueError as error:
        raise ValueError(f"PP_API_PORT must be an integer, got {port_text!r}") from error
    if not 1 <= port <= 65535:
        raise ValueError(f"PP_API_PORT must be between 1 and 65535, got {port}")
    origins = tuple(
        o.strip() for o in source.get("PP_CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()
    )
    return Settings(
        env=source.get("PP_ENV", "development"),
        host=source.get("PP_API_HOST", "127.0.0.1"),
        port=port,
        cors_origins=origins,
        database_url=source.get("PP_DATABASE_URL", ""),
    )
