#!/usr/bin/env bash
set -e
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app:app --host 0.0.0.0 --port 4000 &
python3 agents/risk_agent.py &
python3 agents/yield_agent.py &
python3 agents/execution_agent.py &
python3 agents/coordinator_agent.py &

echo "All processes started. Use logs to verify operation."
