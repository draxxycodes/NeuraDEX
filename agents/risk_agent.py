# agents/risk_agent.py
"""
Risk Agent (uAgents) — listens for chat queries and risk requests, calls the Metta shim,
and replies with an explainable risk assessment.

This agent is built with the uAgents decorator style and exposes a small HTTP
bridge via `backend/agent_router.py` which will call into the agent's local API.

Environment:
- AGENT_NAME (optional)
- AGENT_PORT (default 8001)

Run:
  python3 agents/risk_agent.py
"""
import os
import asyncio
import logging
from uagents import Agent, Context
from metta_engine.metta_shim import assess_portfolio

AGENT_NAME = os.environ.get('RISK_AGENT_NAME', 'risk-agent')
AGENT_PORT = int(os.environ.get('RISK_AGENT_PORT', 8001))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('risk-agent')

risk_agent = Agent(name=AGENT_NAME, port=AGENT_PORT)

@risk_agent.on_message()
async def handle(ctx: Context, sender: str, msg: dict):
    """Generic message handler: expects messages with type and payload."""
    # message contract: {'type':'RISK_ASSESS','payload':{...}}
    mtype = msg.get('type')
    if mtype == 'RISK_ASSESS':
        payload = msg.get('payload', {})
        # payload expected: portfolio_summary
        portfolio = payload.get('portfolio')
        if not portfolio:
            await risk_agent.send(sender, {'error': 'missing portfolio'})
            return
        result = assess_portfolio(portfolio)
        response = {
            'type': 'RISK_RESULT',
            'payload': result
        }
        await risk_agent.send(sender, response)
    elif mtype == 'CHAT_QUERY':
        # simple chat support: user asked "what is my risk?"
        portfolio = msg.get('payload', {}).get('portfolio', {})
        result = assess_portfolio(portfolio)
        reply_text = f"Portfolio risk: {result['portfolio_risk']}. See evidence: {result['evidence']}"
        await risk_agent.send(sender, {'type': 'CHAT_REPLY', 'payload': {'text': reply_text, 'meta': result}})
    else:
        await risk_agent.send(sender, {'error': 'unknown message type'})

if __name__ == '__main__':
    logger.info(f"Starting Risk Agent on port {AGENT_PORT}")
    risk_agent.run()