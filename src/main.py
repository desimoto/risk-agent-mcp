"""
Example orchestrator using FastMCP: Initialize agent, assess sample application.
Flow: Orchestrator → FastMCP Risk Agent → Direct Tool Call → Credit Check → Enriched Reasoning.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load .env for API keys
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from risk_agent_factory import create_risk_agent_with_tools

async def main():
    try:
        # Initialize FastMCP Risk Agent with integrated tools
        agent = create_risk_agent_with_tools()

        # Sample application (extend with real data ingestion)
        sample_app = {
            "business_name": "Tech Startup Inc.",
            "owner_ssn": "123-45-6789",
            "annual_revenue": 75000.0,
            "sector": "Technology",  # Hot sector example
            "loan_amount_requested": 50000.0
        }

        logging.info("Processing loan application with integrated FastMCP tools...")
        result = await agent.assess_loan(sample_app)
        print(f'\n{result}')
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'agent' in locals():
            await agent.close()

if __name__ == "__main__":
    asyncio.run(main())
