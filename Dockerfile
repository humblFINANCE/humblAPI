FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    pkg-config \
    libssl-dev \
    libgtk-3-dev \
    libsoup2.4-dev \
    libjavascriptcoregtk-4.0-dev \
    libwebkit2gtk-4.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

COPY README.md /app/backend/
COPY pyproject.toml poetry.lock* alembic.ini /app/

# Install dependencies without pywry
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Install pywry separately
RUN pip install pywry==0.6.2

COPY backend /app/backend

# ARG WEB_CONCURRENCY
# ENV WEB_CONCURRENCY=${WEB_CONCURRENCY}

EXPOSE 8080
# CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
CMD ["fastapi", "run", "backend/main.py", "--host", "0.0.0.0", "--port", "8080"]