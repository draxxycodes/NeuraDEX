import json
import logging
import threading

from flask import Flask, jsonify, request
from hyperon import MeTTa
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class PortfolioData(Model):
    portfolio: dict


class RiskScore(Model):
    risk_score: str
    explanation: str
    provenance: dict


risk_agent = Agent(
    name="risk_agent",
    port=8001,
    seed="risk_agent_secret_seed",
    endpoint=["http://127.0.0.1:8001/submit"],
)
fund_agent_if_low(risk_agent.wallet.address())

metta = MeTTa()


def load_metta_knowledge_base():
    """Function to load MeTTa facts from file."""
    try:
        metta.run("!(import! &self std)")
        with open("metta/rules/risk_rules.metta", "r") as f:
            facts = f.read()
            metta.run(facts)
        logging.info("MeTTa knowledge base loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading MeTTa knowledge base: {e}")


load_metta_knowledge_base()


@risk_agent.on_message(model=PortfolioData)
async def assess_risk(ctx: Context, sender: str, msg: PortfolioData):
    """Assesses portfolio risk using Python logic and MeTTa facts."""
    try:
        portfolio = msg.portfolio
        assets = portfolio.get("assets", [])
        ctx.logger.info(f"Assessing portfolio: {portfolio}")

        is_volatile = False
        is_concentrated = False
        metta_traces = []

        for asset in assets:
            symbol = asset.get("symbol")
            allocation = asset.get("allocation", 0)

            if allocation > 0.5:
                is_concentrated = True

            assertion = f"!(volatility-of {symbol})"
            result = metta.run(assertion)
            metta_traces.append({"query": assertion, "result": str(result)})

            if result and str(result[0][0]) == "(VolHigh)":
                is_volatile = True

        if is_volatile:
            risk_score = "High"
            explanation = "Portfolio contains highly volatile assets."
        elif is_concentrated:
            risk_score = "High"
            explanation = "Portfolio is highly concentrated in a single asset."
        else:
            risk_score = "Low"
            explanation = "Portfolio has low volatility and is well-diversified."

        provenance = {
            "timestamp": "...",
            "agent": "risk-agent",
            "inputs": {"portfolio": portfolio},
            "metta_trace": metta_traces,
            "computed_score": risk_score,
            "recommended_actions": [],
            # THE FIX: Removed the extra dot after 'wallet'
            "signature": risk_agent.wallet.sign(
                f"{risk_score}:{explanation}".encode()
            ).hex(),
        }
        await ctx.send(
            sender,
            RiskScore(
                risk_score=risk_score, explanation=explanation, provenance=provenance
            ),
        )
        ctx.logger.info(f"Sent risk assessment response: {risk_score}")

    except Exception as e:
        ctx.logger.error(f"Error during risk assessment: {e}")
        await ctx.send(
            sender, RiskScore(risk_score="ERROR", explanation=str(e), provenance={})
        )


app = Flask(__name__)


@app.route("/assess_risk", methods=["POST"])
def assess_risk_endpoint():
    data = request.json
    logging.info(f"Received HTTP request for risk assessment: {data}")
    return jsonify(
        {"status": "assessment_started", "message": "Processing."}
    )


def run_flask():
    app.run(host="0.0.0.0", port=5001)


if __name__ == "__main__":
    # FIX: Corrected indentation for the Flask thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    risk_agent.run()
