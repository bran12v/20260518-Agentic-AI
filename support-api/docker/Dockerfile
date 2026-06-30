# This going to build our Docker Image (runs on docker build)
FROM python:3.12-slim AS builder

WORKDIR /build

COPY pyproject.toml ./
COPY src/ ./src/

RUN python -m venv /opt/venv && /opt/venv/bin/pip install .



# Different stage - (runs on docker run)
FROM python:3.12-slim AS runtime

# Sets the venv bin folder to be in the PATH variable, allowing us to run pip/python/gunicorn etc without specifying the absolute path
# Python buffers stdout - log output gets stuck in a buffer and docker logs shows nothing until the buffer fills or the process exits w/o this var
ENV PATH="/opt/venv/bin:$PATH" PYTHONUNBUFFERED=1 DATA_DIR=/app/data

# Create a group and a user for the docker system to be able to run our python app
RUN groupadd --system --gid 10001 app && useradd --system --uid 10001 --gid 10001 --create-home app 

LABEL org.opencontainers.image.title="support-api" \
    org.opencontainers.image.description="Customer Support Intelligence Platform - backend API." \
    org.opencontainers.image.source="https://github.com/bran12v/20260518-Agentic-AI" \
    org.opencontainers.image.license="MIT"

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY data/ /app/data/

RUN chown -R app:app /app

USER app

# This allows the outside user to use/view port 5000
EXPOSE 5000

# This will allow us to routinely check (officially) the health of our containers
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:5000/live', timeout=2.0).raise_for_status()" || exit 1

# Entrypoint
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--access-logfile", "-", "--error-logfile", "-", "support_api.api:create_app()"]