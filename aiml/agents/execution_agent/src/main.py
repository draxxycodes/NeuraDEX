import logging
import os

import requests
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class TransactionRequest(Model):
    transaction: dict


class TransactionResult(Model):
    success: bool
    transaction_hash: str
    message: str


BACKEND_SIGNING_ENDPOINT = os.getenv(
    "BACKEND_API_URL", "http://localhost:8080/api/sign_transaction"
)

execution_agent = Agent(
    name="execution_agent",
    port=8003,
    seed="execution_agent_secret_seed",
    endpoint=["http://127.0.0.1:8003/submit"],
)
fund_agent_if_low(execution_agent.wallet.address())


@execution_agent.on_message(model=TransactionRequest)
async def compose_and_sign(ctx: Context, sender: str, msg: TransactionRequest):
    """Composes a tx and requests a signature from the secure backend."""
    ctx.logger.info(f"Received transaction request: {msg.transaction}")
    try:
        composed_tx = {
            "from": msg.transaction.get("from"),
            "to": msg.transaction.get("to"),
            "value": msg.transaction.get("value"),
            "data": msg.transaction.get("data"),
        }
        ctx.logger.info(f"Composed transaction: {composed_tx}")
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            BACKEND_SIGNING_ENDPOINT, json=composed_tx, headers=headers
        )

        if response.status_code == 200:
            signed_tx_data = response.json()
            ctx.logger.info("Transaction signed successfully by the backend.")
            await ctx.send(
                sender,
                TransactionResult(
                    success=True,
                    transaction_hash=signed_tx_data.get("transactionHash"),
                    message="Transaction composed and signed.",
                ),
            )
        else:
            await ctx.send(
                sender,
                TransactionResult(
                    success=False,
                    transaction_hash="",
                    message=f"Backend signing failed: {response.text}",
                ),
            )
    except Exception as e:
        ctx.logger.error(f"Error during transaction execution: {e}")
        await ctx.send(
            sender,
            TransactionResult(success=False, transaction_hash="", message=str(e)),
        )


if __name__ == "__main__":
    execution_agent.run()
