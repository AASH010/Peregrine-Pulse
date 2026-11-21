"""Application factory with the health and metadata endpoints (skeleton for task API-01)."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .config import Settings, load_settings

SIMULATION_NOTICE = (
    "PeregrinePulse is a prototype. Incidents, entities and satellite links are simulated and "
    "must not be relied upon in a real emergency."
)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    app = FastAPI(title="PeregrinePulse platform", version=__version__)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/v1/meta")
    def meta() -> dict[str, str]:
        return {
            "name": "PeregrinePulse",
            "version": __version__,
            "environment": settings.env,
            "simulation_notice": SIMULATION_NOTICE,
        }

    return app


app = create_app()
