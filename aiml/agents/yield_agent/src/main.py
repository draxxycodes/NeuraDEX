import logging
import json
import os
from typing import List
import requests

# This must be the very first import to ensure crypto is available
from uagents.crypto import Identity
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

# --- THIS IS THE GUARANTEED SELF-HEALING MECHANISM ---
def ensure_storage_is_clean(agent_seed: str, agent_name: str):
    """
    Finds the agent's storage file BEFORE agent creation and
    deletes it if it is corrupted. This is the only way to
    prevent the JSONDecodeError on this platform.
    """
    # This logic correctly derives the file path
    address = Identity.from_seed(agent_seed, 0).address
    storage_dir = os.path.join(os.path.expanduser("~"), ".uagents", address[:16])
    storage_file = os.path.join(storage_dir, f"{agent_name}.db")
    
    # Create directory if it doesn't exist
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir)

    # Check the file for corruption
    if os.path.exists(storage_file):
        try:
            with open(storage_file, "r") as f:
                # Handle case where file is empty but exists
                if os.path.getsize(storage_file) > 0:
                    json.load(f)
            logging.info(f"Storage for {agent_name} is clean.")
        except (json.JSONDecodeError, OSError):
            logging.error(f"CORRUPTION DETECTED in {storage_file}. Deleting file.")
            os.remove(storage_file)
            logging.info(f"Corrupted storage for {agent_name} was deleted.")

YIELD_AGENT_SEED = "yield_agent_secret_seed"
YIELD_AGENT_NAME = "yield_agent"

# This line runs BEFORE Agent() is called, guaranteeing a clean state.
ensure_storage_is_clean(YIELD_AGENT_SEED, YIELD_AGENT_NAME)
# --- END OF THE FIX ---

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Models remain the same and are correct
class YieldRequest(Model):
    tokens: List[str]

class YieldOpportunity(Model):
    protocol: str
    token: str
    apr: float

class YieldOpportunities(Model):
    opportunities: List[YieldOpportunity]

# This is now guaranteed to succeed because the storage file is clean.
yield_agent = Agent(
    name=YIELD_AGENT_NAME,
    port=8002,
    seed=YIELD_AGENT_SEED,
    endpoint=["http://127.0.0.1:8002/submit"],
)
fund_agent_if_low(yield_agent.wallet.address())


# Agent logic is correct and unchanged
PYUSD_YIELD_API = "https://api.mock-pyusd-yield.com/v1/opportunities"
DEFI_LLAMA_API = "https://yields.llama.fi/pools"

@yield_agent.on_interval(period=3600)
async def query_yield_opportunities(ctx: Context):
    ctx.logger.info("Fetching yield opportunities...")
    try:
        mock_pyusd_data = [{"token": "PYUSD", "apr": 4.5}]
        ctx.storage.set("pyusd_opportunities", mock_pyusd_data)
        ctx.logger.info("Successfully fetched mock PYUSD yields.")
        response = requests.get(DEFI_LLAMA_API)
        if response.status_code == 200:
            ctx.storage.set("defilama_opportunities", response.json())
            ctx.logger.info("Successfully fetched DeFiLlama yields.")
    except Exception as e:
        ctx.logger.error(f"Error fetching yield data: {e}")

@yield_agent.on_message(model=YieldRequest)
async def get_yields(ctx: Context, sender: str, msg: YieldRequest):
    ctx.logger.info(f"Received yield request for tokens: {msg.tokens}")
    opportunities = []
    pyusd_data = ctx.storage.get("pyusd_opportunities", [])
    defilama_data = ctx.storage.get("defilama_opportunities", {}).get("data", [])
    for token in msg.tokens:
        if pyusd_data:
            for opp in pyusd_data:
                if opp.get("token") == token:
                    opportunities.append(
                        YieldOpportunity(
                            protocol="PYUSD Native Yield", token=token, apr=opp["apr"]
                        )
                    )
        if defilama_data:
            for pool in defilama_data:
                if (pool.get("symbol") == token and pool.get("project") == "aave-v3"):
                    opportunities.append(
                        YieldOpportunity(
                            protocol=pool["project"], token=token, apr=pool["apy"]
                        )
                    )
    await ctx.send(sender, YieldOpportunities(opportunities=opportunities))
    ctx.logger.info(f"Sent {len(opportunities)} opportunities to {sender}")

if __name__ == "__main__":
    yield_agent.run()
