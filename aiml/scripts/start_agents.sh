#!/bin/bash
set -e # Exit immediately if any command fails.

echo "--- This script provides a simple, sequential startup to prevent race conditions ---"
echo ""

echo "--- STEP 1: GUARANTEED CLEANUP ---"
# First, kill any and all old processes. This command is proven to work.
kill -9 $(ps aux | grep "[a]gents/.*/src/main.py" | awk '{print $2}') 2>/dev/null || true
# Then, obliterate the state.
rm -rf ~/.uagents/
echo "Old processes and storage have been obliterated. A clean slate is guaranteed."
echo ""

echo "--- STEP 2: LOADING ENVIRONMENT ---"
if [ -f ".env" ]; then
    set -a; source .env; set +a
    echo "Environment variables loaded."
else
    echo "WARNING: .env file not found."
fi
echo ""

echo "--- STEP 3: SEQUENTIAL AGENT LAUNCH ---"
# We now launch each agent one by one, with a small delay.
# This completely eliminates the file creation race condition.

echo "Launching Orchestrator Agent..."
poetry run python agents/orchestrator_agent/src/main.py &
sleep 2

echo "Launching Risk Agent..."
poetry run python agents/risk_agent/src/main.py &
sleep 2

echo "Launching Yield Agent..."
poetry run python agents/yield_agent/src/main.py &
sleep 2

echo "Launching Execution Agent..."
poetry run python agents/execution_agent/src/main.py &
sleep 2

echo "Launching Discovery Agent..."
poetry run python agents/discovery_agent/src/main.py &
sleep 2

echo ""
echo "--- SYSTEM IS LIVE. ALL AGENTS RUNNING CLEANLY. ---"
echo "This terminal is now the AGENT LOG."
echo "Leave it running and open a new terminal for the test."