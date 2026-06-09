# A2A Multi-Agent Architecture

## Overview

This system implements the **A2A Protocol v1.0** (Agent-to-Agent) specification from the Linux Foundation. It enables standardized communication between AI agents using JSON-RPC 2.0.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  (curl, Postman, other agents, web apps)                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP POST (JSON-RPC 2.0)
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌───────────────────┐                 ┌───────────────────┐
│    AGENT A        │                 │    AGENT B        │
│  Data Processor   │                 │    Analyzer       │
│                   │                 │                   │
│ ┌───────────────┐ │                 │ ┌───────────────┐ │
│ │ /a2a/process  │ │◄────A2A────────│ │ call_agent_a  │ │
│ └───────────────┘ │  (when needed)  │ │    (tool)     │ │
│                   │                 │ └───────────────┘ │
│ ┌───────────────┐ │                 │ ┌───────────────┐ │
│ │  Agent Card   │ │                 │ │ /a2a/analyze  │ │
│ └───────────────┘ │                 │ └───────────────┘ │
│                   │                 │                   │
│   Port: 8001      │                 │   Port: 8002      │
└─────────┬─────────┘                 └─────────┬─────────┘
          │                                     │
          └─────────────────┬───────────────────┘
                            │ OpenAI API Compatible
                            ▼
                 ┌─────────────────────┐
                 │   GRAVITEE GATEWAY  │
                 │   (LLM Routing)     │
                 │                     │
                 │ - Rate limiting     │
                 │ - Authentication    │
                 │ - Logging           │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │     LLM PROVIDER    │
                 │  (OpenAI, Azure,    │
                 │   etc.)             │
                 └─────────────────────┘
```

## Component Details

### Agent A - Data Processor

**Purpose**: Independent data processing specialist

**Capabilities**:
- Data cleaning and normalization
- Statistical analysis
- Pattern recognition
- Text processing

**Endpoints**:
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/a2a/process` | POST | Process data via A2A protocol |
| `/health` | GET | Health check (silent) |
| `/.well-known/agent.json` | GET | Agent Card discovery |

**Independence**: Agent A operates fully independently. It does not call other agents.

### Agent B - Analyzer

**Purpose**: Analysis specialist with A2A collaboration capability

**Capabilities**:
- Advanced analysis and insights
- Report generation
- Trend identification
- **Collaboration with Agent A** (when data processing is needed)

**Endpoints**:
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/a2a/analyze` | POST | Analyze via A2A protocol |
| `/health` | GET | Health check (silent) |
| `/.well-known/agent.json` | GET | Agent Card discovery |

**Intelligence**: Agent B decides when to call Agent A:
- Raw data transformation → Calls Agent A
- Data cleaning needed → Calls Agent A
- Simple analysis questions → Handles directly
- Insights without processing → Handles directly

## A2A Protocol v1.0 Compliance

### Message Format

**Request (SendMessage)**:
```json
{
  "jsonrpc": "2.0",
  "method": "SendMessage",
  "params": {
    "message": {
      "messageId": "uuid",
      "role": "ROLE_USER",
      "parts": [{"text": "your message"}],
      "contextId": "optional-context-id"
    }
  },
  "id": 1
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "message": {
      "messageId": "uuid",
      "role": "ROLE_AGENT",
      "parts": [{"text": "agent response"}],
      "contextId": "optional-context-id"
    }
  },
  "id": 1
}
```

### Agent Card

Each agent exposes its capabilities at `/.well-known/agent.json`:

```json
{
  "name": "Agent A - Data Processor",
  "description": "Specialized in data processing...",
  "version": "1.0.0",
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain"],
  "capabilities": {"streaming": false},
  "supportedInterfaces": [{
    "url": "http://localhost:8001/a2a/process",
    "protocolBinding": "JSONRPC",
    "protocolVersion": "1.0"
  }],
  "skills": [...]
}
```

## Communication Flow

### Scenario 1: Direct Request to Agent A

```
Client → Agent A → Gravitee → LLM → Response
```

### Scenario 2: Direct Request to Agent B (no A2A)

```
Client → Agent B → Gravitee → LLM → Response
```

### Scenario 3: Agent B calls Agent A

```
Client → Agent B → (decides needs data processing)
                 → Agent A → Gravitee → LLM → Response to B
                 → Gravitee → LLM → Final Response
         ← Combined analysis
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GRAVITEE_BASE_URL` | Yes | LLM gateway URL |
| `GRAVITEE_API_KEY` | Yes | Gateway API key |
| `GRAVITEE_API_PLATFORM_KEY` | No | Platform key (defaults to API key) |
| `LLM_MODEL` | No | Model identifier |
| `AGENT_A_HOST` | No | Agent A bind host |
| `AGENT_A_PORT` | No | Agent A port (default: 8001) |
| `AGENT_A_URL` | No | Agent A full URL |
| `AGENT_B_HOST` | No | Agent B bind host |
| `AGENT_B_PORT` | No | Agent B port (default: 8002) |
| `AGENT_B_URL` | No | Agent B full URL |

## Logging

### Agent A Terminal Output

```
============================================================
  AGENT A - DATA PROCESSOR
============================================================
  URL:      http://127.0.0.1:8001
  Endpoint: http://127.0.0.1:8001/a2a/process
  LLM:      https://gateway.example.com/llm
  Model:    demo-openai:gpt-4.1
============================================================

[14:32:15] ═══ INCOMING REQUEST ═══
[14:32:15] Caller: Agent B - Analyzer
[14:32:15] Input: Process sales data Q1=100, Q2=200...
[14:32:18] Result: Processed data shows 100% growth...
[14:32:18] ═══ REQUEST COMPLETE ═══
```

### Agent B Terminal Output

```
============================================================
  AGENT B - ANALYZER
============================================================
  URL:        http://127.0.0.1:8002
  Endpoint:   http://127.0.0.1:8002/a2a/analyze
  Agent A:    http://127.0.0.1:8001/a2a/process
  LLM:        https://gateway.example.com/llm
  Model:      demo-openai:gpt-4.1
============================================================

[14:32:15] ═══ INCOMING REQUEST ═══
[14:32:15] Input: Analyze sales data and provide insights...

[14:32:16] ──► CALLING AGENT A ──►
[14:32:16] Endpoint: http://127.0.0.1:8001/a2a/process
[14:32:16] Request: Process sales data Q1=100, Q2=200...
[14:32:18] ◄── RESPONSE: Processed data shows...

[14:32:20] Result: Based on the processed data from Agent A...
[14:32:20] ═══ REQUEST COMPLETE ═══
```

## Security Considerations

1. **No hardcoded credentials** - All secrets in `.env`
2. **Gravitee Gateway** - Handles authentication, rate limiting
3. **CORS configured** - Adjust for production
4. **Internal network** - Agents communicate on internal network

## Scaling

For production deployment:

1. **Horizontal scaling**: Deploy multiple instances behind load balancer
2. **Service discovery**: Use Kubernetes or similar for agent discovery
3. **Agent URLs**: Configure via environment for each deployment
4. **Stateless**: Agents are stateless, can scale independently
