"""
Agent A - Data Processor
A2A Protocol v1.0 compliant agent for data processing and transformation
"""
import uuid
import uvicorn
import os
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
AGENT_A_HOST = os.getenv("AGENT_A_HOST", "127.0.0.1")
AGENT_A_PORT = int(os.getenv("AGENT_A_PORT", "8001"))
AGENT_A_URL = os.getenv("AGENT_A_URL", f"http://{AGENT_A_HOST}:{AGENT_A_PORT}")

# CORS configuration (comma-separated origins, or * for all)
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",") if os.getenv("CORS_ORIGINS") != "*" else ["*"]

# ---------------------------------------------------
# AGENT CARD (A2A v1.0 compliant)
# ---------------------------------------------------
agent_a_card = AgentCard(
    name="Agent A - Data Processor",
    description="Specialized in data processing, transformation, and statistical analysis.",
    version="1.0.0",
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    capabilities=AgentCapabilities(streaming=False),
    supported_interfaces=[
        AgentInterface(
            url=f"{AGENT_A_URL}/a2a/process",
            protocol_binding="JSONRPC",
            protocol_version="1.0"
        ),
    ],
    skills=[
        AgentSkill(
            id="Data_Processing",
            name="Data Processing",
            description="Process and transform data with NLP and statistical analysis.",
            tags=["data", "processing", "analysis"],
            examples=["Process CSV data", "Extract entities from text"],
        )
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
agent_a = Agent(
    client=chat_client,
    name="Agent A - Data Processor",
    instructions="""You are Agent A, a data processing specialist. 
Your role is to process, transform, and analyze data.
You have expertise in:
- Data cleaning and normalization
- Statistical analysis
- Pattern recognition
- Text processing

When processing data, always explain your approach and provide clear results.""",
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
    """Handle A2A JSON-RPC 2.0 requests at /a2a/process"""
    # Check if called by another agent (via header or source info)
    caller = request.headers.get("X-Caller-Agent", "Direct")
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
    
    # Log incoming request with caller info
    print(f"\n[{timestamp}] ═══ INCOMING REQUEST ═══")
    print(f"[{timestamp}] Caller: {caller}")
    print(f"[{timestamp}] Input: {user_input[:150]}{'...' if len(user_input) > 150 else ''}")
    
    try:
        response = await agent_a.run(user_input)
        
        # Get text from last message
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
    return JSONResponse({"status": "healthy", "agent": "Agent A - Data Processor"})


async def agent_card_handler(request: Request) -> JSONResponse:
    """Return A2A agent card at /.well-known/agent.json"""
    # Convert all protobuf types to native Python types
    return JSONResponse({
        "name": str(agent_a_card.name),
        "description": str(agent_a_card.description),
        "version": str(agent_a_card.version),
        "defaultInputModes": list(agent_a_card.default_input_modes),
        "defaultOutputModes": list(agent_a_card.default_output_modes),
        "capabilities": {
            "streaming": bool(agent_a_card.capabilities.streaming) if agent_a_card.capabilities else False
        },
        "supportedInterfaces": [
            {
                "url": str(iface.url),
                "protocolBinding": str(iface.protocol_binding),
                "protocolVersion": str(iface.protocol_version)
            } for iface in list(agent_a_card.supported_interfaces or [])
        ],
        "skills": [
            {
                "id": str(skill.id),
                "name": str(skill.name),
                "description": str(skill.description),
                "tags": list(skill.tags) if skill.tags else [],
                "examples": list(skill.examples) if skill.examples else []
            } for skill in list(agent_a_card.skills or [])
        ]
    })


# ---------------------------------------------------
# SERVER
# ---------------------------------------------------
server = Starlette(
    routes=[
        Route("/health", health_check, methods=["GET"]),
        Route("/.well-known/agent-card.json", agent_card_handler, methods=["GET"]),
        Route("/a2a/process", handle_a2a_request, methods=["POST"]),
        *create_agent_card_routes(agent_a_card),
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
    print("  AGENT A - DATA PROCESSOR")
    print("=" * 60)
    print(f"  URL:      {AGENT_A_URL}")
    print(f"  Endpoint: {AGENT_A_URL}/a2a/process")
    print(f"  LLM:      {config.base_url}")
    print(f"  Model:    {config.model}")
    print("=" * 60)
    uvicorn.run(server, host=AGENT_A_HOST, port=AGENT_A_PORT)
