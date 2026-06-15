# Dockerfile for A2A Agents
FROM python:3.11-slim

# Build argument to select which agent to build (agent_a or agent_b)
ARG AGENT=agent_a
ARG PORT=8001

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AGENT_FILE=${AGENT}.py

WORKDIR /app

# Copy and install pinned dependencies (all versions locked = fast install)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (both agents, simpler approach)
COPY agent_a.py agent_b.py gravitee_config.py ./

# Expose the agent's port
EXPOSE ${PORT}

# Use shell form to allow variable expansion
CMD python ${AGENT_FILE}
