# agents/execution_agent.py
"""
Execution Agent — verifies safety with RiskAgent & YieldAgent before calling backend execution.

This agent demonstrates an execution handshake: it will query RiskAgent and YieldAgent,
collect their replies, and if safe, call the backend execution endpoint (provided by /backend/app.py).

Run:
  python3 agents/execution_agent.py
"""
import os
import logging
import aiohttp
from uagents import Agent, Context

AGENT_NAME = os.environ.get('EXEC_AGENT_NAME', 'execution-agent')
AGENT_PORT = int(os.environ.get('EXEC_AGENT_PORT', 8003))
BACKEND_EXECUTE_URL = os.environ.get('BACKEND_EXECUTE_URL', 'http://backend:4000/api/execute')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('execution-agent')

exec_agent = Agent(name=AGENT_NAME, port=AGENT_PORT)

async def query_agent(agent_addr: str, message: dict):
    pass

@exec_agent.on_message()
async def handle(ctx: Context, sender: str, msg: dict):
    # message: {'type':'EXECUTE_PROPOSAL','payload':{'proposal':{...}, 'portfolio':{...}}}
    mtype = msg.get('type')
    if mtype != 'EXECUTE_PROPOSAL':
        await exec_agent.send(sender, {'error': 'unknown message type'})
        return
    payload = msg.get('payload', {})
    proposal = payload.get('proposal')
    portfolio = payload.get('portfolio')

    # 1) ask RiskAgent for safety
    risk_query = {'type': 'RISK_ASSESS', 'payload': {'portfolio': portfolio}}
    # send to risk-agent
    await exec_agent.send('risk-agent', risk_query)

    # waiting for reply pattern
    async def wait_for_risk():
        # naive wait: in production use event/callback pattern from uAgents
        for _ in range(20):
            msg = await ctx.receive(timeout=2.0)
            if msg and msg.get('type') == 'RISK_RESULT':
                return msg['payload']
        return None

    risk_result = await wait_for_risk()
    if not risk_result:
        await exec_agent.send(sender, {'error': 'risk agent timeout'})
        return
    if risk_result.get('portfolio_risk') == 'HIGH':
        await exec_agent.send(sender, {'type': 'EXEC_REJECTED', 'payload': {'reason': 'RISK_HIGH', 'evidence': risk_result.get('evidence')}})
        return

    # 2) ask YieldAgent for projections (optional)
    yield_query = {'type': 'YIELD_QUERY', 'payload': {'market': payload.get('market', [])}}
    await exec_agent.send('yield-agent', yield_query)

    async def wait_for_yield():
        for _ in range(20):
            msg = await ctx.receive(timeout=2.0)
            if msg and msg.get('type') == 'YIELD_RESULT':
                return msg['payload']
        return None

    yield_result = await wait_for_yield()
    # 3) if safe, call backend to create a signed transaction (backend will require auth)
    if yield_result is None:
        # still proceed but with caution
        reason = 'no_yield_info'
    else:
        reason = 'ok'

    async with aiohttp.ClientSession() as session:
        async with session.post(BACKEND_EXECUTE_URL, json={'proposal': proposal, 'reason': reason}) as resp:
            resp_json = await resp.json()
    await exec_agent.send(sender, {'type': 'EXEC_ACCEPTED', 'payload': resp_json})

if __name__ == '__main__':
    logger.info(f"Starting Execution Agent on port {AGENT_PORT}")
    exec_agent.run()