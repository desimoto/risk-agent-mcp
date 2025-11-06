"""
Factory for creating FastMCPRiskAgent with integrated tools.
This provides a clean interface for setting up the agent with FastMCP tools.
"""

import os
from typing import Optional
from dotenv import load_dotenv

from fastmcp_risk_agent import FastMCPRiskAgent

# Load environment variables
load_dotenv()

def create_risk_agent_with_tools(api_key: Optional[str] = None) -> FastMCPRiskAgent:
    """
    Create a FastMCPRiskAgent with all necessary tools integrated.
    
    Args:
        api_key: Anthropic API key. If None, will try to get from environment.
        
    Returns:
        Configured FastMCPRiskAgent instance
        
    Raises:
        ValueError: If API key is not provided or found in environment
    """
    # Get API key from parameter or environment
    if api_key is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        raise ValueError(
            "Anthropic API key is required. Provide it as parameter or set ANTHROPIC_API_KEY environment variable."
        )
    
    # Import the credit check function
    try:
        from mcp_credit_server import credit_check
    except ImportError as e:
        raise ImportError("Failed to import credit_check function from mcp_credit_server") from e
    
    # Create and return the agent
    return FastMCPRiskAgent(api_key=api_key, credit_check_tool=credit_check)

# Example usage
if __name__ == "__main__":
    import asyncio
    import json
    
    async def main():
        """Example usage of the factory."""
        try:
            # Create agent
            agent = create_risk_agent_with_tools()
            
            # Example loan application
            application = {
                "business_name": "Tech Startup LLC",
                "sector": "Technology", 
                "annual_revenue": 250000,
                "requested_amount": 50000,
                "owner_ssn": "123-45-6789",
                "years_in_business": 2
            }
            
            print("Processing loan application...")
            print(f"Application: {json.dumps(application, indent=2)}")
            
            # Assess the loan
            result = await agent.assess_loan(application)
            print(f"\nAssessment Result:\n{result}")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if 'agent' in locals():
                await agent.close()
    
    asyncio.run(main())