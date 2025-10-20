import logging
import os
import uuid  # Used for dialogue session tracking

from uagents import Agent, Context, Model, Protocol
from uagents.setup import fund_agent_if_low

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class OrchestratorRequest(Model):
    query: str
    user_data: dict


class OrchestratorResponse(Model):
    response: str
    actionable_plan: dict


RISK_AGENT_ADDRESS = os.getenv("RISK_AGENT_ADDRESS")
YIELD_AGENT_ADDRESS = os.getenv("YIELD_AGENT_ADDRESS")

orchestrator_agent = Agent(
    name="orchestrator_agent",
    port=8000,
    seed="orchestrator_agent_secret_seed",
    endpoint=["http://127.0.0.1:8000/submit"],
)
fund_agent_if_low(orchestrator_agent.wallet.address())


# THE FIX: Create a standard Protocol. Dialogues are integrated in this version.
# We will use a unique session ID to track conversations.
orchestrator_protocol = Protocol("Orchestrator")


@orchestrator_protocol.on_message(model=OrchestratorRequest, replies=OrchestratorResponse)
async def handle_request(ctx: Context, sender: str, msg: OrchestratorRequest):
    ctx.logger.info(f"Received request from {sender}: {msg.query}")
    query_lower = msg.query.lower()

    # In a real system, you would await actual responses from these agents.
    # For now, we simulate their answers.
    risk_assessment_result = "Not requested"
    if "risk" in query_lower:
        # Pretend we got a response from the risk agent
        risk_assessment_result = "High Risk - Portfolio is highly concentrated."
        ctx.logger.info("Simulated risk assessment.")

    yield_opportunities_result = []
    if "yield" in query_lower:
        # Pretend we got a response from the yield agent
        yield_opportunities_result = [{"protocol": "Aave", "apr": 5.2}]
        ctx.logger.info("Simulated yield opportunity search.")

    final_response_text = f"Assessment: {risk_assessment_result}"
    actionable_plan_data = {"yields": yield_opportunities_result}

    # THE FIX: We use a simple `await ctx.send()` to reply.
    # The `replies=...` in the decorator handles the session automatically.
    await ctx.send(
        sender,
        OrchestratorResponse(
            response=final_response_text, actionable_plan=actionable_plan_data
        ),
    )
    ctx.logger.info(f"Sent final response back to {sender}")


orchestrator_agent.include(orchestrator_protocol)


if __name__ == "__main__":
    orchestrator_agent.run()
