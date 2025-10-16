# agents/yield_agent.py
"""
Yield Agent — ranks yield opportunities and returns short projections.
This agent is intentionally stateless; it receives market data and returns ranked choices.

Run:
  python3 agents/yield_agent.py
"""
import os
import logging
from uagents import Agent, Context

AGENT_NAME = os.environ.get('YIELD_AGENT_NAME', 'yield-agent')
AGENT_PORT = int(os.environ.get('YIELD_AGENT_PORT', 8002))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('yield-agent')

yield_agent = Agent(name=AGENT_NAME, port=AGENT_PORT)

@yield_agent.on_message()
async def handle(ctx: Context, sender: str, msg: dict):
    # message types: 'YIELD_QUERY'
    mtype = msg.get('type')
    if mtype == 'YIELD_QUERY':
        market = msg.get('payload', {}).get('market', [])
        # market expected: list of {protocol, apy, risk_score}
        # simple ranking: score = apy * (1 - protocol_risk_weight)
        ranked = []
        for item in market:
            apy = float(item.get('apy', 0))
            risk_score = float(item.get('risk_score', 0))
            score = apy * max(0, 1 - risk_score)
            ranked.append({**item, 'score': score})
        ranked.sort(key=lambda x: x['score'], reverse=True)
        await yield_agent.send(sender, {'type': 'YIELD_RESULT', 'payload': {'ranked': ranked[:5]}})
    else:
        await yield_agent.send(sender, {'error': 'unknown message type'})

if __name__ == '__main__':
    logger.info(f"Starting Yield Agent on port {AGENT_PORT}")
    yield_agent.run()