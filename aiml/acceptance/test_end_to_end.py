import asyncio
import os
import uuid
from typing import Dict

from dotenv import load_dotenv
from uagents import Agent, Context, Model, Protocol

load_dotenv()


class OrchestratorRequest(Model):
    query: str
    user_data: Dict


class OrchestratorResponse(Model):
    response: str
    actionable_plan: Dict


ORCHESTRATOR_ADDRESS = os.getenv("ORCHESTRATOR_AGENT_ADDRESS")


# THE FINAL FIX: By explicitly setting a high, unused port number, we guarantee
# there will be no conflict with the orchestrator on port 8000.
test_agent = Agent(
    name="acceptance_test_client",
    seed=f"test_client_seed_{uuid.uuid4()}",
    port=8099
)

final_result = None
test_completed = asyncio.Event()

response_protocol = Protocol("ClientResponseHandler")


@response_protocol.on_message(model=OrchestratorResponse)
async def on_response(ctx: Context, sender: str, msg: OrchestratorResponse):
    global final_result
    ctx.logger.info(f"Received FINAL RESPONSE from {sender}: {msg}")
    final_result = msg
    test_completed.set()


test_agent.include(response_protocol)


async def run_test():
    if not ORCHESTRATOR_ADDRESS:
        print("ERROR: ORCHESTRATOR_AGENT_ADDRESS not found.")
        return

    print("--- Starting End-to-End Acceptance Test ---")
    request = OrchestratorRequest(
        query="Analyze my portfolio risk and find yield for PYUSD.",
        user_data={"portfolio": {}, "tokens": []},
    )

    print(f"Sending request to orchestrator at: {ORCHESTRATOR_ADDRESS}")
    await test_agent.send(ORCHESTRATOR_ADDRESS, request)

    try:
        await asyncio.wait_for(test_completed.wait(), timeout=10.0)
    except asyncio.TimeoutError:
        print("\nTEST FAILED: Timed out waiting for response.")
        return

    print(f"\n--- Test Results ---")
    print(f"Final Response: {final_result.response}")
    success = True
    if "High Risk" not in final_result.response:
        print("FAIL: Expected 'High Risk' in response.")
        success = False
    if "Aave" not in str(final_result.actionable_plan):
        print("FAIL: Expected 'Aave' yield suggestion.")
        success = False

    if success:
        print("\nSUCCESS: All acceptance criteria met.")
    else:
        print("\nTEST FAILED: One or more assertions failed.")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    agent_task = loop.create_task(test_agent.run())

    async def main():
        await asyncio.sleep(2.0)
        await run_test()
        agent_task.cancel()

    main_task = loop.create_task(main())
    try:
        loop.run_until_complete(main_task)
    except asyncio.CancelledError:
        pass
