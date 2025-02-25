FROM python:3.12 as build

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    pkg-config \
    libssl-dev \
    libgtk-3-dev \
    libsoup2.4-dev \
    libjavascriptcoregtk-4.0-dev \
    libwebkit2gtk-4.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry and add it to PATH
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Install the poetry-plugin-export plugin
RUN poetry self add poetry-plugin-export

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"


COPY src src
COPY pyproject.toml poetry.lock* README.md ./

RUN poetry build -f wheel
RUN poetry export --format requirements.txt --output requirements.txt --without-hashes
RUN poetry run pip wheel -w wheels -r requirements.txt
RUN mv dist/* wheels

FROM python:3.12-slim

WORKDIR /app

# Copy dependencies from the previous stage
COPY --from=build /build/wheels /app/wheels

# Set up a virtual environment
RUN python -m venv venv

# Install dependencies
# RUN venv/bin/pip install "uvicorn[standard]"  # TODO: run `poetry add` on me instead
RUN venv/bin/pip install wheels/* --no-deps --no-index

EXPOSE 8080
ENTRYPOINT ["venv/bin/uvicorn", "humblapi.main:app"]
CMD ["--host", "0.0.0.0", "--port", "8080"]