"""
Agent B - Analyzer
A2A Protocol v1.0 compliant agent that collaborates with Agent A
"""
import uuid
import uvicorn
import os
import httpx
from datetime import datetime
from dotenv import load_dotenv

from a2a.server.routes import create_agent_card_routes
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware.cors import CORSMiddleware

from gravitee_config import GraviteeConfig

# Load environment variables
load_dotenv()
os.environ["NO_PROXY"] = "*"

# ---------------------------------------------------
# CONFIGURATION (from environment)
# ---------------------------------------------------
AGENT_B_HOST = os.getenv("AGENT_B_HOST", "127.0.0.1")
AGENT_B_PORT = int(os.getenv("AGENT_B_PORT", "8002"))
AGENT_B_URL = os.getenv("AGENT_B_URL", f"http://{AGENT_B_HOST}:{AGENT_B_PORT}")

# CORS configuration (comma-separated origins, or * for all)
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",") if os.getenv("CORS_ORIGINS") != "*" else ["*"]

# Agent A endpoint for A2A calls
AGENT_A_URL = os.getenv("AGENT_A_URL", "http://127.0.0.1:8001")
AGENT_A_ENDPOINT = f"{AGENT_A_URL}/a2a/process"


# ---------------------------------------------------
# A2A TOOL - Call Agent A (A2A v1.0 compliant)
# ---------------------------------------------------
async def call_agent_a(data_to_process: str) -> str:
    """
    Call Agent A via A2A protocol (v1.0) for data processing.
    
    Use this tool when you need to:
    - Process or transform raw data
    - Clean and normalize data
    - Perform statistical calculations
    - Extract patterns from data
    
    Args:
        data_to_process: The data or request to send to Agent A for processing
        
    Returns:
        The processed response from Agent A
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] ──► CALLING AGENT A ──►")
    print(f"[{timestamp}] Endpoint: {AGENT_A_ENDPOINT}")
    print(f"[{timestamp}] Request: {data_to_process[:100]}{'...' if len(data_to_process) > 100 else ''}")
    
    try:
        # A2A v1.0 compliant SendMessageRequest
        a2a_request = {
            "jsonrpc": "2.0",
            "method": "SendMessage",
            "params": {
                "message": {
                    "messageId": str(uuid.uuid4()),
                    "role": "ROLE_USER",
                    "parts": [{"text": data_to_process}]
                }
            },
            "id": 1
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                AGENT_A_ENDPOINT,
                json=a2a_request,
                headers={"X-Caller-Agent": "Agent B - Analyzer"}
            )
            data = response.json()
            
            if "error" in data:
                error_msg = f"Agent A error: {data['error'].get('message', 'Unknown error')}"
                print(f"[{timestamp}] ◄── ERROR: {error_msg}")
                return error_msg
            
            # A2A v1.0: result contains {message: {...}} or {task: {...}}
            result = data.get("result", {})
            
            # Extract text from A2A Message response
            if isinstance(result, dict) and "message" in result:
                parts = result["message"].get("parts", [])
                for part in parts:
                    if "text" in part:
                        text = part["text"]
                        print(f"[{timestamp}] ◄── RESPONSE: {text[:100]}{'...' if len(text) > 100 else ''}")
                        return text
            
            # Fallback for legacy or unexpected format
            result_str = str(result) if result else "No result from Agent A"
            print(f"[{timestamp}] ◄── RESPONSE: {result_str[:100]}")
            return result_str
            
    except httpx.ConnectError:
        error = f"Error: Could not connect to Agent A at {AGENT_A_ENDPOINT}"
        print(f"[{timestamp}] ◄── CONNECTION ERROR")
        return error
    except Exception as e:
        error = f"Error calling Agent A: {e}"
        print(f"[{timestamp}] ◄── ERROR: {e}")
        return error


# ---------------------------------------------------
# AGENT CARD (A2A v1.0 compliant)
# ---------------------------------------------------
agent_b_card = AgentCard(
    name="Agent B - Analyzer",
    description="Analysis specialist that collaborates with Agent A via A2A protocol.",
    version="1.0.0",
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    capabilities=AgentCapabilities(streaming=False),
    supported_interfaces=[
        AgentInterface(
            url=f"{AGENT_B_URL}/a2a/analyze",
            protocol_binding="JSONRPC",
            protocol_version="1.0"
        )
    ],
    skills=[
        AgentSkill(
            id="Analysis",
            name="Analysis",
            description="Perform advanced analysis and generate insights",
            tags=["analysis", "insights"],
            examples=["Generate reports", "Identify trends"],
        ),
        AgentSkill(
            id="A2A_Collaboration",
            name="A2A Collaboration",
            description="Call Agent A for data processing via A2A protocol",
            tags=["a2a", "collaboration"],
            examples=["Process data with Agent A", "Chain agents"],
        ),
    ],
)

# ---------------------------------------------------
# LLM CLIENT
# ---------------------------------------------------
config = GraviteeConfig()
chat_client = OpenAIChatClient(
    api_key=config.api_key,
    base_url=config.base_url,
    model=config.model,
    default_headers={"x-api-platform-api-key": config.api_platform_key}
)

# ---------------------------------------------------
# AGENT
# ---------------------------------------------------
agent_b = Agent(
    client=chat_client,
    name="Agent B - Analyzer",
    instructions="""You are Agent B, an analysis specialist with access to Agent A.

You have the call_agent_a tool available. Use it ONLY when the task specifically requires:
- Processing or transforming raw data
- Cleaning and normalizing data
- Performing statistical calculations
- Complex data manipulation

For simple analysis, insights, or questions that don't require data processing, 
respond directly WITHOUT calling Agent A.

When you DO need Agent A:
1. Call Agent A with the data processing request
2. Analyze the processed results
3. Generate insights and recommendations

Always provide clear explanations and actionable insights.""",
    tools=[call_agent_a],
)


# ---------------------------------------------------
# HELPER: Extract input from A2A or simple format
# ---------------------------------------------------
def extract_input_from_params(params: dict) -> tuple[str, str | None]:
    """Extract user input and context_id from A2A or simple params format"""
    user_input = ""
    context_id = params.get("message", {}).get("contextId")
    
    # A2A format: params.message.parts[].text
    if "message" in params:
        msg = params["message"]
        parts = msg.get("parts", [])
        for part in parts:
            if "text" in part:
                user_input = part["text"]
                break
    # Simple format fallback: params.input
    elif "input" in params:
        user_input = params["input"]
    
    return user_input, context_id


def create_a2a_response(result_text: str, context_id: str | None = None) -> dict:
    """Create A2A v1.0 compliant response"""
    response = {
        "message": {
            "messageId": str(uuid.uuid4()),
            "role": "ROLE_AGENT",
            "parts": [{"text": result_text}]
        }
    }
    if context_id:
        response["message"]["contextId"] = context_id
    return response


# ---------------------------------------------------
# REQUEST HANDLER (A2A v1.0 compliant)
# ---------------------------------------------------
async def handle_a2a_request(request: Request) -> JSONResponse:
    """Handle A2A JSON-RPC 2.0 requests at /a2a/analyze"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    try:
        body = await request.json()
    except Exception as e:
        return JSONResponse({"jsonrpc": "2.0", "error": {"code": -32700, "message": str(e)}, "id": None})
    
    request_id = body.get("id")
    params = body.get("params", {})
    
    user_input, context_id = extract_input_from_params(params)
    
    if not user_input:
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {"code": -32602, "message": "Invalid params: message.parts[].text or input required"},
            "id": request_id
        })
    
    print(f"\n[{timestamp}] ═══ INCOMING REQUEST ═══")
    print(f"[{timestamp}] Input: {user_input[:150]}{'...' if len(user_input) > 150 else ''}")
    
    try:
        response = await agent_b.run(user_input)
        
        # Get text from last message (tool calls may be in earlier messages)
        result_text = ""
        if hasattr(response, 'messages') and response.messages:
            result_text = response.messages[-1].text or ""
        if not result_text:
            result_text = str(response)
        
        print(f"[{timestamp}] Result: {result_text[:150]}{'...' if len(result_text) > 150 else ''}")
        print(f"[{timestamp}] ═══ REQUEST COMPLETE ═══\n")
        
        return JSONResponse({
            "jsonrpc": "2.0", 
            "result": create_a2a_response(result_text, context_id), 
            "id": request_id
        })
        
    except Exception as e:
        print(f"[{timestamp}] ERROR: {e}")
        return JSONResponse({"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": request_id})


async def health_check(request: Request) -> JSONResponse:
    """Simple health check - no logging"""
    return JSONResponse({"status": "healthy", "agent": "Agent B - Analyzer"})


# ---------------------------------------------------
# SERVER
# ---------------------------------------------------
server = Starlette(
    routes=[
        Route("/health", health_check, methods=["GET"]),
        Route("/a2a/analyze", handle_a2a_request, methods=["POST"]),
        *create_agent_card_routes(agent_b_card),
        # Keep root for backward compatibility
        Route("/", handle_a2a_request, methods=["POST"]),
    ]
)

server.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    print("=" * 60)
    print("  AGENT B - ANALYZER")
    print("=" * 60)
    print(f"  URL:        {AGENT_B_URL}")
    print(f"  Endpoint:   {AGENT_B_URL}/a2a/analyze")
    print(f"  Agent A:    {AGENT_A_ENDPOINT}")
    print(f"  LLM:        {config.base_url}")
    print(f"  Model:      {config.model}")
    print("=" * 60)
    uvicorn.run(server, host=AGENT_B_HOST, port=AGENT_B_PORT)
