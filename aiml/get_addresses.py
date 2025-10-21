from uagents import Agent

agents_config = [
    ("orchestrator_agent", "orchestrator_agent_secret_seed", 8005),
    ("risk_agent", "risk_agent_secret_seed", 8001),
    ("yield_agent", "yield_agent_secret_seed", 8002),
    ("execution_agent", "execution_agent_secret_seed", 8003),
    ("discovery_agent", "discovery_agent_secret_seed", 8004),
]

print("\nAgent Addresses:")
print("=" * 80)
for name, seed, port in agents_config:
    agent = Agent(name=name, seed=seed, port=port)
    print(f"{name.upper()}_ADDRESS=\"{agent.address}\"")
print("=" * 80)
