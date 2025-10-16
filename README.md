# 🧠 NeuraDEX: Multi-Agent DeFi Portfolio Orchestrator

> **"Autonomous, explainable, and risk-aware DeFi portfolio management — powered by ASI Alliance, uAgents, and MeTTa reasoning."**

---

## 🚀 Overview

**NeuraDEX** is an **AI-driven, multi-agent DeFi portfolio orchestrator** designed for the **ASI Alliance track**.  
It unites **Fetch.ai’s uAgents**, **SingularityNET’s MeTTa symbolic reasoning**, and a **FastAPI backend** into one powerful, transparent, and autonomous ecosystem.

Through conversational AI and autonomous agents, NeuraDEX enables users to:
- 🧭 Analyze portfolio risk intelligently  
- 📈 Discover yield opportunities across chains  
- 🤖 Generate explainable execution proposals  
- 🧮 Reason symbolically using MeTTa for transparency  

---

## 🧩 Core Architecture

### 🧠 AI/ML & Agent Layer (`/agents`)

| Agent | Role | Description |
|:------|:------|:-------------|
| **`risk_agent.py`** | Risk Analyzer | Evaluates volatility/liquidity using MeTTa symbolic reasoning |
| **`yield_agent.py`** | Yield Optimizer | Finds high-yield protocols for PYUSD and other assets |
| **`execution_agent.py`** | Executor | Simulates or prepares signed transaction proposals |
| **`coordinator_agent.py`** | Orchestrator | Coordinates all agents, ensuring consensus and response flow |

Agents communicate via **uAgents** and are compatible with the **ASI:One Chat Protocol** and **Agentverse** registry.

---

### ⚙️ Backend Layer (`/backend`)

Built using **FastAPI**, the backend:
- Serves as an **API gateway** between agents and frontend/UI  
- Simulates **transaction execution and validation**  
- Aggregates and returns portfolio and yield data  

**Endpoints**
| Endpoint | Method | Description |
|:----------|:--------|:-------------|
| `/api/portfolio_summary` | `GET` | Returns portfolio composition, volatility, and liquidity |
| `/api/execute` | `POST` | Accepts execution proposals and simulates signing |

---

### 🧮 Reasoning Layer (`/metta_engine`)

Implements **symbolic reasoning** using **MeTTa (SingularityNET)**.

- `rules.json`: Symbolic rules for portfolio risk evaluation  
- `metta_shim.py`: Python ↔ MeTTa interface  
- `__init__.py`: Initialization and utilities  

**Example rule logic**
```metta
(risk_score (volatility > 0.10) => "HIGH")
(risk_score (liquidity_ratio < 0.3) => "MEDIUM")
```
This ensures every decision has explainability and provenance.

---

## 🏗️ Infrastructure & Scripts

| Folder | Purpose |
|:--------|:----------|
| `/infra` | Deployment setup and environment configs |
| `/scripts` | Orchestration scripts (`run_all.sh` to start all agents and backend) |
| `/venv` | Virtual environment |
| `requirements.txt` | Dependency definitions |

---

## 🧬 Tech Stack

| Layer | Technologies |
|:-------|:--------------|
| **AI & Agents** | Fetch.ai **uAgents**, **MeTTa** reasoning |
| **Backend** | FastAPI, Uvicorn, Pydantic |
| **Language** | Python 3.11+ |
| **Infrastructure** | Docker, Shell Scripts, `.env` configuration |
| **Integrations** | ASI:One, Agentverse, PYUSD |
| **Future** | Avail Nexus, Blockscout SDK, Envio HyperSync |

---

## ⚡ Quick Start

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/draxxycodes/NeuraDEX.git
cd NeuraDEX
```

### 2️⃣ Setup Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3️⃣ Run the System
```bash
bash scripts/run_all.sh
```
This script:
	•	🚀 Starts all uAgents (risk, yield, execution, coordinator)
	•	🌐 Launches FastAPI backend on http://localhost:4000

---

## 🧪 Example API Usage

### ➤ Portfolio Summary

```bash
curl -X GET http://localhost:4000/api/portfolio_summary
```
Response:
```bash
{
  "assets": [
    {"symbol": "PYUSD", "fraction": 0.4, "volatility": 0.01, "liquidity_ratio": 0.9}
  ],
  "aggregates": {"volatility": 0.16}
}
```

### ➤ Execute Transaction

```bash
curl -X POST http://localhost:4000/api/execute -H "Content-Type: application/json" \
-d '{"proposal": {"rebalance_to": "USDC"}, "reason": "reduce volatility"}'
```
Response:
```bash
{
  "signed_tx": "0xdeadbeefcafebabe",
  "status": "simulated",
  "proposal": {"rebalance_to": "USDC"},
  "reason": "reduce volatility"
}
```

---

## 🧠 How the AI Works

### 🔹 Step 1 — Data Ingestion
The **backend** aggregates real-time DeFi data and distributes it to all active agents for reasoning and collaboration.  
This ensures that every agent operates with synchronized market data, portfolio states, and user-defined constraints.

### 🔹 Step 2 — Symbolic Reasoning
The **`risk_agent`** leverages **MeTTa** (from SingularityNET) to reason over symbolic rules defined in `rules.json`.  
Using MeTTa’s structured logic and pattern-matching capabilities, it produces **explainable, human-readable reasoning traces** for its risk decisions.

**Example MeTTa rule logic**
```metta
(risk_score (volatility > 0.10) => "HIGH")
(risk_score (liquidity_ratio < 0.3) => "MEDIUM")
(risk_score (stablecoin > 0.5) => "LOW")
```

### 🔹 Step 3 — Multi-Agent Collaboration

The **`coordinator_agent`** acts as the communication bridge between all other agents.  
It requests inputs from the **`risk_agent`** and **`yield_agent`**, merges their outputs, and formulates a unified decision proposal.  
This collaborative reasoning allows **NeuraDEX** to provide **dynamic, adaptive, and transparent DeFi strategies** that evolve intelligently with market conditions.

### 🔹 Step 4 — Execution

The **`execution_agent`** simulates secure transaction signing and proposal submission through the backend’s `/api/execute` endpoint.  
This agent ensures that all transaction recommendations are **verified, logged, and auditable**, maintaining safety, reproducibility, and compliance with decentralized financial standards.

---

## 🌐 Integration with ASI Alliance

**NeuraDEX** is fully aligned with the **Artificial Superintelligence (ASI) Alliance** technology stack — merging **autonomy, reasoning, and interoperability** across intelligent decentralized systems.

| Technology | Role |
|:------------|:------|
| **uAgents (Fetch.ai)** | Enables agent autonomy, messaging, and discoverability |
| **MeTTa (SingularityNET)** | Provides structured reasoning and symbolic knowledge graphs |
| **ASI:One Chat Protocol** | Facilitates natural-language conversations with agents |
| **Agentverse** | Hosts and lists agents for discoverability and orchestration |

---

## 🔗 References

- [🔗 Fetch.ai Innovation Lab Docs](https://innovationlab.fetch.ai/resources/docs/intro)  
- [🔗 uAgents Creation Guide](https://innovationlab.fetch.ai/resources/docs/agent-creation/uagent-creation)  
- [🔗 Agent Communication Guide](https://innovationlab.fetch.ai/resources/docs/agent-communication/uagent-uagent-communication)  
- [🔗 MeTTa Python Tutorials](https://metta-lang.dev/docs/learn/tutorials/python_use/metta_python_basics.html)  
- [🔗 ASI:One Platform](https://asi1.ai)  
- [🔗 Agentverse Documentation](https://docs.agentverse.ai/documentation/advanced-usages/agentverse-mcp)

---

## 🧾 Project Structure

```bash
NeuraDEX/
├── agents/
│   ├── coordinator_agent.py       # Orchestrates agent communication
│   ├── execution_agent.py         # Simulates & signs transaction proposals
│   ├── risk_agent.py              # Performs portfolio risk analysis via MeTTa
│   ├── yield_agent.py             # Identifies best yield opportunities
│
├── backend/
│   ├── app.py                     # FastAPI backend entrypoint
│   ├── agent_router.py            # Agent communication endpoints
│
├── metta_engine/
│   ├── metta_shim.py              # Python–MeTTa bridge interface
│   ├── rules.json                 # Symbolic reasoning rule base
│
├── infra/                         # Deployment and configuration files
│
├── scripts/
│   ├── run_all.sh                 # Starts all agents and backend
│
├── requirements.txt               # Python dependencies
├── .env                           # Environment configuration variables
└── README.md                      # Main documentation
```

---

## 🧩 Future Roadmap

| Feature | Status |
|:---------|:--------|
| Agentverse listing with MCP manifest | 🔄 In Progress |
| ASI:One conversational interface | 🔄 In Progress |
| Cross-chain sync via Avail Nexus SDK | 🧩 Planned |
| Blockscout SDK integration | 🧩 Planned |
| Envio HyperSync analytics | 🧩 Planned |
| PostgreSQL portfolio persistence | 🧩 Planned |

---

## 🛡️ Security & Ethics

- 🔒 **No private keys** are stored in code or logs.  
- 🧩 All **transaction proposals** are simulated or require manual signing.  
- 🪶 Each reasoning step includes a **provenance trace** for full explainability.  
- 📜 Full transparency maintained with **human-interpretable reasoning logs**.  

---

## 👨‍💻 Contributors

| Role | Name | Responsibilities |
|:------|:------|:------------------|
| **Full-Stack Lead** | — | React Frontend + Integration |
| **Backend Engineer** | — | Smart Contracts + FastAPI |
| **AI/ML Specialist** | 🧠 | uAgents, MeTTa, ASI Integration |
| **Integration Specialist** | — | Avail Nexus, Blockscout, Deployment |

---

## 🏆 Prize Track Alignment

| Prize Track | Technology Used | Status |
|:--------------|:----------------|:--------|
| **ASI Alliance ($10,000)** | uAgents, MeTTa, ASI:One | ✅ Fully Implemented |
| **Avail Nexus ($10,000)** | SDK Integration | 🔄 Partial |
| **PYUSD ($10,000)** | Stablecoin Yield Logic | ✅ Done |
| **Blockscout SDK ($5,000)** | Transaction Notifications | 🔄 Planned |
| **Envio HyperSync ($5,000)** | Telemetry Integration | 🔄 Planned |

---

## 🧰 Development Notes

### 🧪 Run Backend Only
```bash
python3 backend/app.py
```
### 🧩 Run Individual Agent
To run any specific agent manually for debugging or testing:
```bash
python3 agents/risk_agent.py
```

### View Logs
Monitor live agent or backend logs in real time:
```bash
tail -f logs/agent.log
```

## 📖 License
Licensed under the Apache License 2.0.
You may freely use, modify, and distribute this project with proper attribution.
```bash
Copyright 2025 NeuraDEX
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:
http://www.apache.org/licenses/LICENSE-2.0
```
Unless required by applicable law or agreed to in writing, software distributed under the License is provided on an “AS IS” BASIS, without warranties or conditions of any kind, either express or implied.
See the License for the specific language governing permissions and limitations under the License.

## 💠 Tagline
### NeuraDEX — Autonomous Finance, Human Trust.
**Built with ❤️ by Team NeuraDEX for the ASI Alliance Hackathon 2025.**
© 2025 All Rights Reserved.