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

# Copy project files
COPY pyproject.toml poetry.lock* README.md /app/

# Install dependencies without pywry
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Install pywry separately
RUN pip install pywry==0.6.2

# Copy the rest of the application
COPY . /app

EXPOSE 8080
CMD ["fastapi", "run", "src/humblapi/main.py", "--host", "0.0.0.0", "--port", "8080"]