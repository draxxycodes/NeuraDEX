import asyncio
import logging
from uagents import Agent, Context

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

discovery_agent = Agent(
    name="discovery_agent",
    port=8004,
    seed="discovery_agent_secret_seed",
)

@discovery_agent.on_event("startup")
async def startup_message(ctx: Context):
    """Logs a message to confirm the agent has started successfully."""
    ctx.logger.info("Discovery Agent is alive and running.")
    ctx.logger.info("External registration is DISABLED as Almanac endpoint is not available.")

@discovery_agent.on_interval(period=60)
async def local_health_check(ctx: Context):
    """Periodically logs a health check message."""
    # In a real system, this agent would ping the other local agents.
    # For now, this confirms the agent's event loop is active.
    ctx.logger.info("Performing routine local health check... System is alive.")


if __name__ == "__main__":
    discovery_agent.run()
