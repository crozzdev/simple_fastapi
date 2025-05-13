# An example using multi-stage image builds to create a final image without uv.

# First, build the application in the `/app` directory.
# See `Dockerfile` for details.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Disable Python downloads, because we want to use the system interpreter
# across both images. If using a managed Python version, it needs to be
# copied from the build image into the final image; see `standalone.Dockerfile`
# for an example.
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# Then, use a final image without uv
FROM python:3.12-slim-bookworm
# It is important to use the image that matches the builder, as the path to the
# Python executable must be the same, e.g., using `python:3.11-slim-bookworm`
# will fail.

# Install SQL Server ODBC Driver dependencies
# Set apt to not use proxy
RUN echo 'Acquire::http::Pipeline-Depth "0";' > /etc/apt/apt.conf.d/99no-pipeline && \
    echo 'Acquire::http::No-Cache=True;' >> /etc/apt/apt.conf.d/99no-pipeline && \
    echo 'Acquire::BrokenProxy=true;' >> /etc/apt/apt.conf.d/99no-pipeline

# Clear any potential proxy settings
ENV http_proxy="" https_proxy="" HTTP_PROXY="" HTTPS_PROXY=""

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gnupg \
    curl \
    unixodbc \
    unixodbc-dev \
    apt-transport-https && \
    # Add Microsoft repository - with explicit key handling
    curl --noproxy '*' -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-archive-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
    msodbcsql18 && \
    # Clean up
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the application from the builder
COPY --from=builder --chown=app:app /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Set database environment variables
# These should be overridden in production with docker -e options
ENV DB_USER=sa
ENV DB_PASSWORD=Password123
ENV DB_SERVER=host.docker.internal
ENV DB_PORT=1433
ENV DB_NAME=heroesdb

# Add a non-root user for the application
RUN addgroup --system app && \
    adduser --system --ingroup app app

# Switch to non-root user
USER app

# Run the FastAPI application by default using the fastapi CLI
CMD ["fastapi", "dev", "--host", "0.0.0.0", "/app/src/main.py"]