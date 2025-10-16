# metta_engine/metta_shim.py
"""
A lightweight MeTTa-compatible reasoning shim. This provides a small rule engine that accepts facts
and executes the rules in `rules.json` to return a decision and a derivation trace.

This file intentionally exposes the same minimal API your agents will call:

- initialize(engine_config)
- assert_facts(facts: dict)
- query(query_name: str) -> dict

In production, this shim can be swapped for a real MeTTa/Hyperon endpoint. We keep the API
surface small so replacement is straightforward: the agents call metta_client = MettaClient(base_url=...)
and then use metta_client.assess_portfolio(...)

Citations / docs:
- MeTTa language overview: https://metta-lang.dev/ and OpenCog Hyperon materials cited in project docs.
"""
import json
import os
from typing import Dict, Any, List

RULES_PATH = os.path.join(os.path.dirname(__file__), "rules.json")

class MettaShim:
    def __init__(self, rules_path: str = RULES_PATH):
        with open(rules_path, 'r') as f:
            config = json.load(f)
        self.rules = config.get('rules', [])

    def assess_portfolio(self, portfolio_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Assess portfolio and return {level, evidence, scores}
        Expects portfolio_summary to have:
        - holdings: list of {symbol, fraction, volatility, liquidity_ratio}
        - aggregated metrics (optional)
        """
        evidence: List[str] = []
        highest = "LOW"
        for hold in portfolio_summary.get('holdings', []):
            # attach normalized metrics
            fraction = float(hold.get('fraction', 0))
            vol = float(hold.get('volatility', 0))
            liq_ratio = float(hold.get('liquidity_ratio', 1.0))
            for rule in self.rules:
                cond = rule['condition']
                f = cond['field']
                ok = False
                if cond['type'] == 'gt' and f == 'volatility':
                    ok = vol > cond['value']
                if cond['type'] == 'lt' and f == 'liquidity_ratio':
                    ok = liq_ratio < cond['value']
                if cond['type'] == 'gt' and f == 'holding_fraction':
                    ok = fraction > cond['value']
                if ok:
                    # apply effect
                    effect = rule['effect']
                    level = effect.get('risk', 'LOW')
                    evidence.append(f"{hold.get('symbol')} -> {effect.get('explanation')}")
                    # simple priority ordering HIGH > MEDIUM > LOW
                    if level == 'HIGH':
                        highest = 'HIGH'
                    elif level == 'MEDIUM' and highest != 'HIGH':
                        highest = 'MEDIUM'
        # include aggregated heuristics if present
        agg = portfolio_summary.get('aggregates', {})
        # if aggregate volatility exists, also consider it
        agg_vol = float(agg.get('volatility', 0))
        if agg_vol > 0.18:
            evidence.append(f"Portfolio aggregate volatility {agg_vol} > 0.18")
            highest = 'HIGH'
        return {
            'portfolio_risk': highest,
            'evidence': evidence,
            'raw': portfolio_summary
        }

# convenience wrapper used by agents
metta_client = MettaShim()

def assess_portfolio(portfolio_summary: Dict[str, Any]) -> Dict[str, Any]:
    return metta_client.assess_portfolio(portfolio_summary)