#!/usr/bin/env bash
# convenience script to run all components locally (non-docker)
set -e
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
# run backend, then agents in separate terminals (tmux/screen recommended)
# backend
uvicorn backend.app:app --host 0.0.0.0 --port 4000 &
# agents (run each in its own terminal ideally)
python3 agents/risk_agent.py &
python3 agents/yield_agent.py &
python3 agents/execution_agent.py &
python3 agents/coordinator_agent.py &

echo "All processes started. Use logs to verify operation."
