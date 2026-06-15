# Dockerfile for A2A Agent A - Data Processor
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files for uv sync
COPY pyproject.toml uv.lock ./

# Sync dependencies from lock file (fast - no resolution needed)
RUN uv sync --frozen --no-dev

# Copy application code
COPY agent_a.py gravitee_config.py ./

# Agent A listens on port 8001
EXPOSE 8001

CMD ["uv", "run", "python", "agent_a.py"]
