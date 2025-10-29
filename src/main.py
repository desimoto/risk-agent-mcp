"""
Example orchestrator using FastMCP: Initialize agent, assess sample application.
Flow: Orchestrator → FastMCP Risk Agent → HTTP Call → Credit Check → Enriched Reasoning.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env for API keys
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from fastmcp_risk_agent import FastMCPRiskAgent

async def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("Set ANTHROPIC_API_KEY in .env or env var.")

    # Initialize FastMCP Risk Agent with default localhost:8000 URL
    agent = FastMCPRiskAgent(api_key)

    # Sample application (extend with real data ingestion)
    sample_app = {
        "business_name": "Tech Startup Inc.",
        "owner_ssn": "111-11-1111",
        "annual_revenue": 75000.0,
        "sector": "Technology",  # Hot sector example
        "loan_amount_requested": 50000.0
    }

    try:
        result = await agent.assess_loan(sample_app)
        print("Risk Assessment:\n", result)
    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(main())
