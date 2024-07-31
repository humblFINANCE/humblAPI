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

## 🌟 Features

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