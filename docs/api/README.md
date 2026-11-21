# API documentation

The platform server currently exposes two endpoints (skeleton, task API-01):

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/api/v1/meta` | Name, version, environment and the simulation notice |

While the server runs, FastAPI serves interactive documentation at `/docs` and the OpenAPI document at `/openapi.json`. A published, reviewed API description arrives with task API-09, after the ingestion, status and acknowledgment endpoints exist.
