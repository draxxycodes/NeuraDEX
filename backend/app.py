# backend/app.py
"""
FastAPI app that exposes agent endpoints used by the frontend. It also hosts
small helper endpoints for local testing: /api/portfolio/summary and /api/execute
(used by the Execution agent to obtain a signed tx payload from your wallet service).

To run locally:
    uvicorn app:app --host 0.0.0.0 --port 4000 --reload

Environment variables can point to agent containers if you run with docker-compose.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .agent_router import router as agent_router

app = FastAPI(title='ASI AI/ML Specialist Backend')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

app.include_router(agent_router, prefix='/api')

# Small local test endpoints
class PortfolioSummary(BaseModel):
    address: str

@app.get('/api/portfolio/summary')
async def portfolio_summary(address: str = 'test'):
    # this endpoint returns a sample summary used by agents during dev and demo
    sample = {
        'address': address,
        'holdings': [
            {'symbol': 'TOKENA', 'fraction': 0.35, 'volatility': 0.28, 'liquidity_ratio': 0.05},
            {'symbol': 'TOKENB', 'fraction': 0.25, 'volatility': 0.08, 'liquidity_ratio': 0.5},
            {'symbol': 'PYUSD', 'fraction': 0.40, 'volatility': 0.01, 'liquidity_ratio': 0.9}
        ],
        'aggregates': {'volatility': 0.16}
    }
    return sample

class ExecutePayload(BaseModel):
    proposal: dict
    reason: str

@app.post('/api/execute')
async def execute_transaction(payload: ExecutePayload):
    signed_tx = {
        'signed_tx': '0xdeadbeefcafebabe',
        'status': 'simulated',
        'proposal': payload.proposal,
        'reason': payload.reason
    }
    return signed_tx

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 4000)))
