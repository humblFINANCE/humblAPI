# AGENTS.md - humblAPI

FastAPI service that wraps the `humbldata` Python library and exposes it over REST. Part of the humblFINANCE ecosystem: `humblDATA` (library) -> **humblAPI** (this repo, HTTP service) -> `humblFINANCE` (Next.js frontend). Deployed on Render.

## Stack

- Python `>=3.11,<3.13`, FastAPI, served by uvicorn (dev) / gunicorn (prod).
- Package manager: `uv` (canonical `uv.lock`; a legacy `poetry.lock` also exists but `uv` is the source of truth).
- Task runner: `poethepoet` (`poe <task>`).
- Depends on `humbldata` from PyPI (pinned `humbldata>=1.22.1`) - not the local sibling checkout.

## Run / test / lint

- Install: `uv sync --all-groups`.
- Run dev server: `uv run poe api --dev` (uvicorn `--reload` on `0.0.0.0:8000`). Non-dev `poe api` uses gunicorn.
- Tests: `uv run pytest` (or `uv run poe test` for coverage).
- Env: `cp .env.example .env` (defaults to `ENVIRONMENT=development`).

## Cursor Cloud specific instructions

The startup update script already runs `uv sync --all-groups` here. To run/test:

- **Routes are served under the `/api/v1` prefix**, not root. `GET /` and `GET /health` 404; use `GET /api/v1/health`, `GET /api/v1/latest-price?symbols=AAPL`, `GET /api/v1/humblMOMENTUM?symbols=AAPL`, etc. (`GET /openapi.json` lists them all).
- **Requires a local Redis on `localhost:6379`** (dev connects to `db=1` for FastAPICache + FastAPILimiter, see `main.py` lifespan). Redis is installed in the VM - start it if not running, e.g. `redis-server --port 6379` (backgrounded). The app still boots without Redis (errors are caught/logged) but caching + rate limiting won't work and `/api/v1/redis-health` fails.
- **Data endpoints need network**: `latest-price`, `humblCHANNEL`, `humblMOMENTUM`, `humblCOMPASS` flow through `humbldata` to the hosted OpenBB Platform API at `https://data.humblfinance.io` (there is no local OpenBB in the default stack).
- Copy `.env.example` to `.env` before running (not committed).
