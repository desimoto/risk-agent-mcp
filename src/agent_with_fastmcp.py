"""
Example usage of FastMCPRiskAgent with FastMCP integration.
This demonstrates how to use the agent with direct FastMCP function calls.
"""

import asyncio
import json
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from fastmcp_risk_agent import FastMCPRiskAgent
# Import the MCP server to access the credit_check function
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mcp_credit_server import credit_check

async def main():
    """Example usage of the refactored FastMCPRiskAgent."""
    
    # Initialize the agent with Anthropic API key and credit check function
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    
    # Create the agent with the credit check function
    agent = FastMCPRiskAgent(api_key=api_key, credit_check_tool=credit_check)
    
    # Example loan application
    application = {
        "business_name": "Tech Startup LLC",
        "sector": "Technology",
        "annual_revenue": 250000,
        "requested_amount": 50000,
        "owner_ssn": "123-45-6789",
        "years_in_business": 2
    }
    
    try:
        print("Processing loan application...")
        print(f"Application: {json.dumps(application, indent=2)}")
        
        # Assess the loan
        result = await agent.assess_loan(application)
        print(f"\nAssessment Result:\n{result}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(main())