# backend/agent_router.py
"""
This thin router translates HTTP requests from the frontend into uAgents messages by making
HTTP calls to a small local bridge or by using the Agent's HTTP endpoints if available.

For simplicity and to keep the code self-contained, this router acts as the authoritative
backend API: it accepts chat queries and executes the proper message flow.

Important: in production you may run your agents in separate containers and adjust the
addresses/ports with environment variables.
"""
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx

router = APIRouter()

AGENT_COORDINATOR_URL = os.environ.get('COORDINATOR_AGENT_HTTP', 'http://localhost:8004')
AGENT_EXEC_URL = os.environ.get('EXEC_AGENT_HTTP', 'http://localhost:8003')

class ChatRequest(BaseModel):
    user_id: str
    text: str
    portfolio: dict = {}
    market: list = []

@router.post('/agent/chat')
async def agent_chat(req: ChatRequest):
    # Forward to coordinator agent by posting to its HTTP receive endpoint (uAgents supports an HTTP REST shim in many deployments)
    # We'll assume the coordinator agent exposes an incoming HTTP bridge at /api/incoming
    coordinator_incoming = f"{AGENT_COORDINATOR_URL}/api/incoming"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(coordinator_incoming, json={'type': 'CHAT', 'payload': {'text': req.text, 'portfolio': req.portfolio, 'market': req.market}, 'sender': req.user_id})
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        # If we cannot reach the agent via HTTP bridge, fallback to direct agent-to-agent pattern
        raise HTTPException(status_code=500, detail=f"Coordinator agent unreachable: {e}")
    return data

class ExecuteRequest(BaseModel):
    user_id: str
    proposal: dict
    portfolio: dict
    market: list = []

@router.post('/agent/execute')
async def agent_execute(req: ExecuteRequest):
    execution_incoming = f"{AGENT_EXEC_URL}/api/incoming"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(execution_incoming, json={'type': 'EXECUTE_PROPOSAL', 'payload': {'proposal': req.proposal, 'portfolio': req.portfolio, 'market': req.market}, 'sender': req.user_id})
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution agent unreachable: {e}")
