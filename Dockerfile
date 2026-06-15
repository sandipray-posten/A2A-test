# Dockerfile for A2A Agent A - Data Processor
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy and install pinned dependencies (all versions locked = fast install)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agent_a.py gravitee_config.py ./

# Agent A listens on port 8001
EXPOSE 8001

CMD ["python", "agent_a.py"]
