# Testing A2A Agents

This guide shows how to test Agent A and Agent B using curl commands.

## Prerequisites

Start both agents in separate terminals:

```bash
# Terminal 1
uv run python agent_a.py

# Terminal 2
uv run python agent_b.py
```

---

# terminal 3
# Health check
Invoke-WebRequest -Uri "http://localhost:8001/health" | Select-Object -ExpandProperty Content

# Test Agent B → Agent A chain
Invoke-WebRequest -Uri "http://localhost:8002/a2a/analyze" -Method POST -ContentType "application/json" -Body '{"jsonrpc": "2.0", "method": "analyze", "params": {"input": "Process Q1=100, Q2=200 and analyze"}, "id": 1}' | Select-Object -ExpandProperty Content

## GET Requests

### Health Check - Agent A

```bash
curl http://localhost:8001/health
```

**Response:**
```json
{"status": "healthy", "agent": "Agent A - Data Processor"}
```

### Health Check - Agent B

```bash
curl http://localhost:8002/health
```

**Response:**
```json
{"status": "healthy", "agent": "Agent B - Analyzer"}
```

### Agent Card - Agent A

```bash
curl http://localhost:8001/.well-known/agent.json
```

### Agent Card - Agent B

```bash
curl http://localhost:8002/.well-known/agent.json
```

---

## POST Requests

### Agent A - Data Processing

#### A2A v1.0 Format (Recommended)

```bash
curl -X POST http://localhost:8001/a2a/process \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "SendMessage",
    "params": {
      "message": {
        "messageId": "test-123",
        "role": "ROLE_USER",
        "parts": [{"text": "Process this data: 10, 20, 30, 40, 50. Calculate sum and average."}]
      }
    },
    "id": 1
  }'
```

#### Simple Format (Backward Compatible)

```bash
curl -X POST http://localhost:8001/a2a/process \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "process",
    "params": {"input": "Clean and normalize this text: HELLO   world  123"},
    "id": 1
  }'
```

### Agent B - Analysis

#### A2A v1.0 Format (Recommended)

```bash
curl -X POST http://localhost:8002/a2a/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "SendMessage",
    "params": {
      "message": {
        "messageId": "test-456",
        "role": "ROLE_USER",
        "parts": [{"text": "Analyze sales data: Q1=100, Q2=200, Q3=150, Q4=300. Provide insights and trends."}]
      }
    },
    "id": 1
  }'
```

#### Simple Format

```bash
curl -X POST http://localhost:8002/a2a/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "analyze",
    "params": {"input": "What are the key trends in this data: Jan=50, Feb=75, Mar=60?"},
    "id": 1
  }'
```

---

## Git Bash / Linux Commands (Recommended for curl)

**Important:** If you're behind a corporate proxy, set NO_PROXY first:

```bash
export NO_PROXY="*"
```

### Health Check

```bash
curl --noproxy '*' http://127.0.0.1:8001/health --output -
curl --noproxy '*' http://127.0.0.1:8002/health --output -
```

### POST to Agent A

```bash
export NO_PROXY="*"
curl -X POST http://127.0.0.1:8001/a2a/process -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"process","params":{"input":"Calculate sum of 10, 20, 30"},"id":1}' --output -
```

### POST to Agent B (may call Agent A)

```bash
export NO_PROXY="*"
curl -X POST http://127.0.0.1:8002/a2a/analyze -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"analyze","params":{"input":"Analyze Q1=100, Q2=200"},"id":1}' --output -
```

### A2A v1.0 Format

```bash
export NO_PROXY="*"
curl -X POST http://127.0.0.1:8002/a2a/analyze -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"SendMessage","params":{"message":{"messageId":"test-1","role":"ROLE_USER","parts":[{"text":"Analyze Q1=100, Q2=200 and give insights"}]}},"id":1}' --output -
```

---

## Windows PowerShell Commands

### Health Check

```powershell
Invoke-WebRequest -Uri "http://localhost:8001/health" -Method GET | Select-Object -ExpandProperty Content
```

### POST to Agent A

```powershell
$body = @{
    jsonrpc = "2.0"
    method = "SendMessage"
    params = @{
        message = @{
            messageId = "test-123"
            role = "ROLE_USER"
            parts = @(@{text = "Process data: 10, 20, 30"})
        }
    }
    id = 1
} | ConvertTo-Json -Depth 5

Invoke-WebRequest -Uri "http://localhost:8001/a2a/process" -Method POST -ContentType "application/json" -Body $body | Select-Object -ExpandProperty Content
```

### POST to Agent B

```powershell
$body = @{
    jsonrpc = "2.0"
    method = "SendMessage"
    params = @{
        message = @{
            messageId = "test-456"
            role = "ROLE_USER"
            parts = @(@{text = "Analyze Q1=100, Q2=200 and give insights"})
        }
    }
    id = 1
} | ConvertTo-Json -Depth 5

Invoke-WebRequest -Uri "http://localhost:8002/a2a/analyze" -Method POST -ContentType "application/json" -Body $body | Select-Object -ExpandProperty Content
```

### Simple Format (PowerShell)

```powershell
# Agent A
Invoke-WebRequest -Uri "http://localhost:8001/a2a/process" -Method POST -ContentType "application/json" -Body '{"jsonrpc": "2.0", "method": "process", "params": {"input": "Sum of 1,2,3,4,5"}, "id": 1}' | Select-Object -ExpandProperty Content

# Agent B
Invoke-WebRequest -Uri "http://localhost:8002/a2a/analyze" -Method POST -ContentType "application/json" -Body '{"jsonrpc": "2.0", "method": "analyze", "params": {"input": "What trends in Q1=50, Q2=100?"}, "id": 1}' | Select-Object -ExpandProperty Content
```

---

## Test Scenarios

### 1. Agent A Only (Data Processing)

```bash
curl -X POST http://localhost:8001/a2a/process \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "SendMessage",
    "params": {
      "message": {
        "messageId": "scenario-1",
        "role": "ROLE_USER",
        "parts": [{"text": "Extract all numbers from: The price is $150 and quantity is 25 units"}]
      }
    },
    "id": 1
  }'
```

### 2. Agent B Only (No A2A Call)

Simple analysis that Agent B handles directly:

```bash
curl -X POST http://localhost:8002/a2a/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "SendMessage",
    "params": {
      "message": {
        "messageId": "scenario-2",
        "role": "ROLE_USER",
        "parts": [{"text": "What is the capital of France?"}]
      }
    },
    "id": 1
  }'
```

### 3. Agent B Calls Agent A (A2A Chain)

Request that triggers Agent B to call Agent A for data processing:

```bash
curl -X POST http://localhost:8002/a2a/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "SendMessage",
    "params": {
      "message": {
        "messageId": "scenario-3",
        "role": "ROLE_USER",
        "parts": [{"text": "Process and analyze this raw sales data: Jan:$1000, Feb:$1500, Mar:$1200, Apr:$1800. First clean the data, then provide trend analysis."}]
      }
    },
    "id": 1
  }'
```

Watch Agent A terminal - you should see the incoming request from Agent B!

---

## Expected Response Format

### A2A v1.0 Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "message": {
      "messageId": "uuid-here",
      "role": "ROLE_AGENT",
      "parts": [{"text": "Agent response text here..."}]
    }
  },
  "id": 1
}
```

### Error Response

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32602,
    "message": "Invalid params: message.parts[].text or input required"
  },
  "id": 1
}
```

---

## Endpoints Summary

| Agent | Endpoint | Method | Description |
|-------|----------|--------|-------------|
| A | `/health` | GET | Health check |
| A | `/.well-known/agent.json` | GET | Agent Card |
| A | `/a2a/process` | POST | Data processing |
| A | `/` | POST | Root (same as /a2a/process) |
| B | `/health` | GET | Health check |
| B | `/.well-known/agent.json` | GET | Agent Card |
| B | `/a2a/analyze` | POST | Analysis |
| B | `/` | POST | Root (same as /a2a/analyze) |
