"""
Example orchestrator: Initialize agent, assess sample application.
Flow: Orchestrator → Risk Agent → MCP Call → Experian API → Enriched Reasoning.
"""

import asyncio
import os
# print(os.getcwd()) 
os.chdir(os.path.dirname(__file__))  # Ensure relative paths work
# print("new wd=="+os.getcwd()) 

# Load .env for API keys
from dotenv import load_dotenv
load_dotenv()

from risk_agent import RiskAgent

async def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("Set ANTHROPIC_API_KEY in .env or env var.")

    # Check Experian creds (optional; will error in tool if missing)
    if not all(os.getenv(k) for k in ["EXPERIAN_USERNAME", "EXPERIAN_PASSWORD", "EXPERIAN_CLIENT_ID", "EXPERIAN_CLIENT_SECRET"]):
        print("Warning: Experian env vars not set; tool will fallback to neutral score.")

    agent = RiskAgent(api_key)
    await agent.initialize_mcp()

    # Sample application (extend with real data ingestion)
    sample_app = {
        "business_name": "Tech Startup Inc.",
        "owner_ssn": "123-45-6789",  # Use test SSN from Experian sandbox docs
        "annual_revenue": 75000.0,
        "sector": "Technology",  # Hot sector example
        "loan_amount_requested": 50000.0
    }

    result = await agent.assess_loan(sample_app)
    print("Risk Assessment:\n", result)

    await agent.close()

if __name__ == "__main__":
    asyncio.run(main())