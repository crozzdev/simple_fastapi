# Simple FastAPI Hero API

A RESTful API built with FastAPI and SQLModel for managing superhero data, with Microsoft SQL Server database integration.

## 🚀 Features

- CRUD operations for superhero data
- SQL Server integration using SQLModel ORM
- Dockerized application for easy deployment
- Environment-based configuration

## 📋 Prerequisites

- Python 3.8+
- Microsoft SQL Server (with ODBC Driver 18)
- Docker (optional, for containerized deployment)
- uv package manager (for dependency management)

> **Note**: The example database credentials in this README are for demonstration purposes only. In a production environment, you should implement proper credentials management and avoid exposing sensitive information.

## 🔧 Installation

### Local Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/simple_fastapi.git
   cd simple_fastapi
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install uv
   uv sync
   ```

4. Create a `.env` file in the project root with your database configuration:

   ```env
   DB_USER=your_db_user
   DB_PASSWORD=your_password
   DB_SERVER=your_server_address
   DB_PORT=1433
   DB_NAME=your_database
   ```

5. Run the application:

   ```bash
   uvicorn src.main:app --reload
   ```

### Docker Deployment

This project uses a multi-stage Docker build process to create an optimized and smaller final image:

- First stage uses `uv` to manage dependencies and build the application
- Second stage creates a clean deployment image without build tools
- SQL Server ODBC drivers are properly installed for database connectivity

1. Build the Docker image:

   ```bash
   docker build -t simple_fastapi .
   ```

2. Run the container:

   ```bash
   docker run -d --name simple_fastapi -p 8000:8000 --env-file .env simple_fastapi
   ```

> **⚠️ Security Warning**: The `.env` file approach shown above is suitable for development only. For production deployments, use proper secrets management solutions like Docker Secrets, Kubernetes Secrets, or a dedicated vault service. Never commit sensitive credentials to version control or embed them directly in your Docker images.

## 🔍 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Welcome message |
| POST | /heroes/ | Create a new hero |
| GET | /heroes/ | Get a list of heroes with pagination |

## 📦 Project Structure

```text
simple_fastapi/
├── Dockerfile          # Docker configuration for deployment
├── pyproject.toml      # Project metadata and dependencies
├── README.md           # Project documentation
├── uv.lock             # Dependency lock file
└── src/
    ├── __init__.py
    ├── main.py                 # FastAPI application entry point
    └── simple_db_connection.py # Database connection utilities
```

## 🛠️ Technologies Used

- [FastAPI](https://fastapi.tiangolo.com/): High-performance web framework
- [SQLModel](https://sqlmodel.tiangolo.com/): ORM for SQL databases with Pydantic integration
- [Pydantic](https://pydantic-docs.helpmanual.io/): Data validation and settings management
- [MS SQL Server](https://www.microsoft.com/en-us/sql-server): Database
- [Docker](https://www.docker.com/): Containerization
- [uv](https://github.com/astral-sh/uv): Fast Python package installer and resolver

## 🧪 Development

For development work, you can install additional packages:

```bash
uv sync --dev
```

## 📄 License

This project is licensed under the MIT License.