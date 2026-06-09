# A2A Protocol Multi-Agent System

A2A Protocol v1.0 compliant multi-agent system with two collaborative agents. Uses Gravitee API Gateway for LLM routing.

## Features

- **A2A Protocol v1.0** compliant JSON-RPC communication
- **Agent A** - Data Processor (independent)
- **Agent B** - Analyzer (can call Agent A when needed)
- **Gravitee Gateway** integration for LLM routing
- **Environment-based configuration** for production deployment

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

### 1. Install uv (if not installed)

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone & Setup

```bash
git clone <repository-url>
cd a2a-agent-test

# Copy environment template
cp .env.example .env
```

### 3. Configure Environment

Edit `.env` with your credentials:

```env
# Agent URLs (for production, use actual hostnames)
AGENT_A_HOST=127.0.0.1
AGENT_A_PORT=8001
AGENT_A_URL=http://127.0.0.1:8001

AGENT_B_HOST=127.0.0.1
AGENT_B_PORT=8002
AGENT_B_URL=http://127.0.0.1:8002

# Gravitee Gateway (REQUIRED)
GRAVITEE_BASE_URL=https://your-gateway.com/llm
GRAVITEE_API_KEY=your-api-key
GRAVITEE_API_PLATFORM_KEY=your-platform-key

# LLM Model
LLM_MODEL=demo-openai:gpt-4.1
```

### 4. Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 5. Run Agents

**Terminal 1 - Start Agent A:**
```bash
uv run python agent_a.py
```

**Terminal 2 - Start Agent B:**
```bash
uv run python agent_b.py
```

## API Endpoints

### Agent A (Data Processor)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/a2a/process` | POST | A2A data processing endpoint |
| `/.well-known/agent.json` | GET | Agent Card |

### Agent B (Analyzer)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/a2a/analyze` | POST | A2A analysis endpoint |
| `/.well-known/agent.json` | GET | Agent Card |

## Example Requests

### Direct Request to Agent A

```bash
curl -X POST http://localhost:8001/a2a/process \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "SendMessage",
    "params": {
      "message": {
        "messageId": "123",
        "role": "ROLE_USER",
        "parts": [{"text": "Process this data: 10, 20, 30, 40"}]
      }
    },
    "id": 1
  }'
```

### Request to Agent B (may call Agent A)

```bash
curl -X POST http://localhost:8002/a2a/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "SendMessage",
    "params": {
      "message": {
        "messageId": "456",
        "role": "ROLE_USER",
        "parts": [{"text": "Analyze sales data Q1=100, Q2=200, Q3=150 and provide insights"}]
      }
    },
    "id": 1
  }'
```

### Simple Format (Backward Compatible)

```bash
curl -X POST http://localhost:8002/a2a/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "analyze",
    "params": {"input": "What trends do you see in Q1=100, Q2=200?"},
    "id": 1
  }'
```

## Docker Deployment

```bash
docker-compose up --build
```

## Production Deployment

1. Set environment variables for production URLs:
   ```env
   AGENT_A_URL=https://agent-a.your-domain.com
   AGENT_B_URL=https://agent-b.your-domain.com
   ```

2. Configure Gravitee credentials securely (use secrets management)

3. Deploy agents as separate services

## Project Structure

```
a2a-agent-test/
├── agent_a.py           # Agent A - Data Processor
├── agent_b.py           # Agent B - Analyzer
├── gravitee_config.py   # Gravitee gateway configuration
├── pyproject.toml       # uv/pip dependencies
├── requirements.txt     # Legacy pip requirements
├── .env                 # Environment configuration
├── .env.example         # Environment template
├── docker-compose.yml   # Docker deployment
├── Dockerfile           # Container build
├── README.md            # This file
└── ARCHITECTURE.md      # Architecture details
```

## License

MIT
