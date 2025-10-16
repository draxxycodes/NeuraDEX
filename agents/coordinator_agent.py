# agents/coordinator_agent.py
"""
Coordinator agent: exposes a simple entrypoint that receives user chat queries (via ASI:One chat protocol),
routes them to the correct domain agent, and composes a human-friendly reply.

Run:
  python3 agents/coordinator_agent.py
"""
import os
import logging
from uagents import Agent, Context

AGENT_NAME = os.environ.get('COORDINATOR_AGENT_NAME', 'coordinator-agent')
AGENT_PORT = int(os.environ.get('COORDINATOR_AGENT_PORT', 8004))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('coordinator-agent')

coord_agent = Agent(name=AGENT_NAME, port=AGENT_PORT)

@coord_agent.on_message()
async def handle(ctx: Context, sender: str, msg: dict):
    # Expect CHAT messages from frontend: {type:'CHAT', payload:{text, portfolio, context}}
    mtype = msg.get('type')
    if mtype != 'CHAT':
        await coord_agent.send(sender, {'error': 'unknown message type'})
        return
    text = msg.get('payload', {}).get('text', '').lower()
    portfolio = msg.get('payload', {}).get('portfolio', {})

    if 'risk' in text:
        # delegate to risk-agent
        await coord_agent.send('risk-agent', {'type': 'RISK_ASSESS', 'payload': {'portfolio': portfolio}})
        # wait for result
        res = await ctx.receive(timeout=5.0)
        if res and res.get('type') == 'RISK_RESULT':
            payload = res.get('payload')
            reply = f"Portfolio risk: {payload.get('portfolio_risk')}. Evidence: {payload.get('evidence')}"
            await coord_agent.send(sender, {'type': 'CHAT_REPLY', 'payload': {'text': reply, 'meta': payload}})
        else:
            await coord_agent.send(sender, {'type': 'CHAT_REPLY', 'payload': {'text': 'Risk agent timed out.'}})
    elif 'yield' in text:
        await coord_agent.send('yield-agent', {'type': 'YIELD_QUERY', 'payload': {'market': msg.get('payload', {}).get('market', [])}})
        res = await ctx.receive(timeout=5.0)
        if res and res.get('type') == 'YIELD_RESULT':
            ranked = res['payload'].get('ranked', [])
            reply = 'Top yield opportunities: ' + ', '.join([f"{r['protocol']}(@{r['apy']}%)" for r in ranked[:3]])
            await coord_agent.send(sender, {'type': 'CHAT_REPLY', 'payload': {'text': reply, 'meta': {'ranked': ranked}}})
        else:
            await coord_agent.send(sender, {'type': 'CHAT_REPLY', 'payload': {'text': 'Yield agent timed out.'}})
    else:
        # default fallback: forward to Risk Agent for simple diagnostics
        await coord_agent.send('risk-agent', {'type': 'RISK_ASSESS', 'payload': {'portfolio': portfolio}})
        res = await ctx.receive(timeout=5.0)
        if res and res.get('type') == 'RISK_RESULT':
            payload = res.get('payload')
            reply = f"I couldn't parse your intent exactly. Best guess: Portfolio risk is {payload.get('portfolio_risk')}" 
            await coord_agent.send(sender, {'type': 'CHAT_REPLY', 'payload': {'text': reply, 'meta': payload}})
        else:
            await coord_agent.send(sender, {'type': 'CHAT_REPLY', 'payload': {'text': 'I could not process your request.'}})

if __name__ == '__main__':
    logger.info(f"Starting Coordinator Agent on port {AGENT_PORT}")
    coord_agent.run()