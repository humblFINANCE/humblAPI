# 🏦 humblFINANCE Backend

## 📋 Description

humblFINANCE Backend is a FastAPI-based backend service for the humblFINANCE web app. It provides the necessary API endpoints and data processing capabilities to support the financial operations of the humblFINANCE platform.

## 🛠️ Tech Stack

- 🐍 Python 3.11
- 🚀 FastAPI
- 🗃️ SQLModel (ORM)
- 🔄 Alembic (Database migrations)
- 📊 humbldata (Custom data library)
- 🏗️ Poetry (Dependency management)
- 🐳 Docker (Containerization)

## 🌟 Features.

- RESTful API endpoints for financial data
- Database integration with SQLModel
- Asynchronous operations support
- Configurable settings for different environments


## 🚀 Getting Started

1. Clone the repository
   ```
   git clone https://github.com/humblfinance/humblfinance-backend.git
   ```
2. Install dependencies:
   ```
   poetry install
   ```
3. Set up your environment variables
   ```
   cp .env.example .env
   ```
4. Build and run the Docker container:
   ```
   docker build -t humblfinance-api .
   docker run -p 8080:8080 humblfinance-api
   ```
5. Alternatively, run the application directly:
   ```
   uvicorn backend.main:app --host 0.0.0.0 --port 8080

   ## OR ##

   fastapi run backend/main.py --host 0.0.0.0 --port 8080
   ```
## 📡 API Endpoints

### Core Endpoints
- `GET /` - Welcome endpoint
- `GET /health` - Health check endpoint
- `GET /redis-health` - Redis connection health check
- `GET /flush-redis` - Flush Redis database or FastAPI cache (requires API token)

### Portfolio Endpoints
- `GET /portfolio` - Get portfolio data for specified symbols
  - Query params: `symbols` (default: "AAPL,NVDA,TSLA"), `membership` (default: "humblPEON")

### OpenBB Endpoints
- `GET /latest-price` - Get latest price data for specified symbols
  - Query params: `symbols`, `provider` (default: "yfinance")
- `GET /last-close` - Get last closing price for specified symbols
  - Query params: `symbols`, `provider` (default: "yfinance")

### Toolbox Endpoints

#### humblCHANNEL
- `GET /humblCHANNEL` - Get Mandelbrot Channel data
  - Query params: `symbols`, `interval`, `start_date`, `end_date`, `provider`, `window`, `rv_adjustment`, `rv_method`, `rs_method`, `rv_grouped_mean`, `yesterday_close`, `historical`, `chart`, `template`, `membership`

#### humblMOMENTUM
- `GET /humblMOMENTUM` - Get momentum analysis data
  - Query params: `symbols`, `method` (log/simple/shift), `window`, `chart`, `template`, `start_date`, `end_date`, `membership`

## 🐳 Docker Support

The application can be containerized using Docker. Build and run the Docker image using the provided Dockerfile.

## 🧪 Development

- Linting: Ruff
- Type checking: MyPy
- Documentation: MkDocs

The FastAPI app uses fastapi-cache2 for caching. This stores cached values in a local redis DB when in development mode, and in a remote redis DB when in production mode (vercel kv).
Please make sure that your local redis DB is running, or that the remote redis DB is available, before running the app.

## 📚 Documentation

For more detailed information, refer to the MkDocs-generated documentation.

## 👥 Contributors

- jjfantini <jenningsfantini@gmail.com>

## 📄 License

Attribution-NonCommercial-ShareAlike 4.0 International