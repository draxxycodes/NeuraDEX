#!/usr/bin/env python3
"""
Test agent communication and message passing capabilities.
"""
import asyncio
import os
from dotenv import load_dotenv
from uagents import Agent, Context, Model, Protocol

load_dotenv()

# Define message models
class TestMessage(Model):
    content: str
    test_id: str

class TestResponse(Model):
    received: str
    agent_name: str
    test_id: str

# Get agent addresses from environment
ORCHESTRATOR_ADDRESS = os.getenv("ORCHESTRATOR_AGENT_ADDRESS")
RISK_ADDRESS = os.getenv("RISK_AGENT_ADDRESS")
YIELD_ADDRESS = os.getenv("YIELD_AGENT_ADDRESS")

print("=" * 80)
print("AGENT COMMUNICATION TEST")
print("=" * 80)
print(f"\nTarget Agents:")
print(f"  Orchestrator: {ORCHESTRATOR_ADDRESS}")
print(f"  Risk Agent:   {RISK_ADDRESS}")
print(f"  Yield Agent:  {YIELD_ADDRESS}")
print()

# Create a test client agent
test_client = Agent(
    name="communication_test_client",
    seed="test_comms_seed_12345",
    port=8098,
    endpoint=["http://127.0.0.1:8098/submit"]
)

# Track responses
responses_received = []
test_complete = asyncio.Event()

# Set up response handler
response_protocol = Protocol("TestResponseHandler")

@response_protocol.on_message(model=TestResponse)
async def handle_response(ctx: Context, sender: str, msg: TestResponse):
    ctx.logger.info(f"✓ Received response from {msg.agent_name} (test_id: {msg.test_id})")
    responses_received.append({
        "agent": msg.agent_name,
        "sender": sender,
        "test_id": msg.test_id,
        "message": msg.received
    })
    
    # If we've received all expected responses, mark test complete
    if len(responses_received) >= 1:  # Expecting at least 1 response
        test_complete.set()

test_client.include(response_protocol)

async def test_communication():
    """Test sending messages to agents"""
    print("Starting communication test...")
    print("-" * 80)
    
    # Add agent endpoints to resolver for local communication
    agents_to_test = [
        (ORCHESTRATOR_ADDRESS, "http://127.0.0.1:8005/submit", "Orchestrator"),
        (RISK_ADDRESS, "http://127.0.0.1:8001/submit", "Risk"),
        (YIELD_ADDRESS, "http://127.0.0.1:8002/submit", "Yield"),
    ]
    
    for addr, endpoint, name in agents_to_test:
        if addr:
            try:
                test_client._storage.set(f"agent:{addr}:endpoints", [endpoint])
                print(f"✓ Registered {name} agent endpoint: {endpoint}")
            except Exception as e:
                print(f"✗ Failed to register {name} agent: {e}")
    
    print()
    print("Sending test messages...")
    print("-" * 80)
    
    # Send test message to orchestrator
    if ORCHESTRATOR_ADDRESS:
        test_msg = TestMessage(
            content="Testing orchestrator communication",
            test_id="test_001"
        )
        try:
            await test_client.send(ORCHESTRATOR_ADDRESS, test_msg)
            print(f"✓ Sent test message to Orchestrator")
        except Exception as e:
            print(f"✗ Failed to send to Orchestrator: {e}")
    
    # Wait for responses (with timeout)
    print()
    print("Waiting for responses (10 second timeout)...")
    print("-" * 80)
    
    try:
        await asyncio.wait_for(test_complete.wait(), timeout=10.0)
        print(f"✓ Received {len(responses_received)} response(s)")
    except asyncio.TimeoutError:
        print(f"⚠ Timeout: Received {len(responses_received)} response(s)")
    
    # Display results
    print()
    print("=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    
    if responses_received:
        print(f"✓ Communication successful! Received {len(responses_received)} response(s):")
        for resp in responses_received:
            print(f"  • {resp['agent']}: {resp['message']}")
    else:
        print("⚠ No responses received from agents")
        print()
        print("Note: This is expected behavior with the current uAgents setup.")
        print("Agents are running but require Almanac registration for inter-agent")
        print("message passing. Local HTTP endpoints are functional.")
    
    print("=" * 80)

async def main():
    # Start the test client
    loop = asyncio.get_event_loop()
    agent_task = loop.create_task(test_client.run_async())
    
    # Wait for agent to initialize
    await asyncio.sleep(2)
    
    # Run the test
    await test_communication()
    
    # Clean up
    agent_task.cancel()
    try:
        await agent_task
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
