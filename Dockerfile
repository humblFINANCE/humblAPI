# # Use Python base image for better compatibility with binary packages like polars
# FROM python:3.12-slim

# WORKDIR /app

# # Install system dependencies needed for building Python packages
# RUN apt-get update && apt-get install -y \
#     curl \
#     gcc \
#     g++ \
#     && rm -rf /var/lib/apt/lists/*

# # Install uv
# COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# # Copy all necessary files for the build
# COPY uv.lock pyproject.toml README.md ./
# COPY src ./src

# # Install dependencies and project in a virtual environment
# RUN uv venv .venv
# RUN uv sync --locked --no-dev

# # Activate the virtual environment
# ENV PATH="/app/.venv/bin:$PATH"

# # Expose port
# EXPOSE 8080

# # Run the FastAPI application
# CMD ["fastapi", "run", "--host", "0.0.0.0", "--port", "8080", "src/humblapi/main.py"]


FROM python:3.12-slim-bookworm AS base
FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:0.4.9 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
COPY uv.lock pyproject.toml /app/
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-install-project --no-dev
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-dev
FROM base
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8080
CMD ["uvicorn", "humblapi.main:app", "--host", "0.0.0.0", "--port", "8080"]

# https://depot.dev/docs/container-builds/how-to-guides/optimal-dockerfiles/python-uv-dockerfile