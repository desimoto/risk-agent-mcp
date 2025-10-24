"""
Core ReAct agent for loan risk assessment using FastMCP.
Uses Claude for reasoning and FastMCP for tool execution.
Stateful via message history.
"""

import json
from typing import List, Dict, Any, Optional
import httpx
from anthropic import Client
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

class CreditInput(BaseModel):
    """Credit check input schema."""
    ssn: str = Field(..., description="Applicant's Social Security Number")
    business_revenue: float = Field(..., description="Annual business revenue")

class CreditOutput(BaseModel):
    """Credit check output schema."""
    credit_score: int = Field(..., description="FICO score (300-850)")
    risk_level: str = Field(..., description="Risk level: low/medium/high")
    approved_limit: float = Field(..., description="Suggested loan limit")
    notes: str = Field(..., description="Risk notes")

class FastMCPRiskAgent:
    def __init__(self, api_key: str, mcp_server_url: str = "http://localhost:8000"):
        """Initialize agent with Anthropic API key and MCP server URL."""
        self.client = Client(api_key=api_key)
        self.model = "claude-haiku-4-5-20251001"
        self.messages: List[Dict[str, Any]] = []
        self.mcp_url = mcp_server_url
        self.http_client = httpx.AsyncClient()

    def _tools_to_schemas(self) -> List[Dict[str, Any]]:
        """Convert tool schemas for Anthropic."""
        return [{
            "type": "custom",
            "name": "credit_check",
            "description": "Check applicant's credit score and assess risk level",
            "input_schema": {
                "type": "object",
                "properties": {
                    "ssn": {
                        "type": "string",
                        "description": "Applicant's Social Security Number (XXX-XX-XXXX format)"
                    },
                    "business_revenue": {
                        "type": "number",
                        "description": "Annual business revenue in USD"
                    }
                },
                "required": ["ssn", "business_revenue"]
            }
        }]

    async def _call_mcp_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Call FastMCP tool via HTTP."""
        try:
            response = await self.http_client.post(
                f"{self.mcp_url}/{name}",
                json=arguments,
                headers={"Content-Type": "application/json"},
                timeout=10.0  # Add timeout
            )
            response.raise_for_status()
            result = response.json()
            
            # Format the result for better readability
            formatted_result = {
                "credit_score": result.get("credit_score"),
                "risk_level": result.get("risk_level"),
                "approved_limit": f"${result.get('approved_limit', 0):,.2f}",
                "notes": result.get("notes")
            }
            return json.dumps(formatted_result, indent=2)
        except httpx.TimeoutException:
            return "Tool error: Request timed out"
        except httpx.HTTPError as e:
            return f"Tool error: HTTP error occurred: {str(e)}"
        except Exception as e:
            return f"Tool error: Unexpected error: {str(e)}"

    async def assess_loan(self, application_data: Dict[str, Any]) -> str:
        """Process a loan application and provide a risk assessment."""
        self.messages = [{
            "role": "user",
            "content": (
                "Please assess this small business loan application:\n"
                f"{json.dumps(application_data, indent=2)}\n\n"
                "Use the credit_check tool to get the applicant's credit score and risk assessment."
            )
        }]

        system_prompt = """You are an expert Risk Agent for small business loans. Your task is to:

1. Call the credit_check tool with:
   - ssn: The owner's SSN from owner_ssn field
   - business_revenue: The annual revenue from annual_revenue field

2. Analyze all factors including:
   - Credit score from the tool response
   - Business sector and associated risks
   - Revenue vs. requested loan amount
   - Approved limit from credit check
   - Any risk flags or notes

3. Provide a final assessment as a JSON object:
   {
     "risk_level": ["low", "medium", or "high"],
     "recommendation": ["approve", "deny", or "need_more_info"],
     "reason": "Clear explanation of the decision"
   }

Important: 
- Format numbers for readability (e.g., $50,000.00)
- Consider sector volatility (tech/crypto need higher scrutiny)
- Be decisive but thorough in your assessment"""

        max_steps = 5  # Prevent infinite loops
        for step in range(max_steps):
            tools_schemas = self._tools_to_schemas()
            print(f"Step {step} messages:", json.dumps(self.messages, indent=2))
            print("Tools:", json.dumps(tools_schemas, indent=2))
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.1,
                system=system_prompt,
                tools=tools_schemas if tools_schemas else None,
                messages=self.messages
            )
            print("Response:", message.content)
            
            # Handle the model's response
            for content in message.content:
                if content.type == "text":
                    # Add text to messages
                    self.messages.append({"role": "assistant", "content": content.text})
                    # Check if it's a final assessment
                    if '"risk_level":' in content.text and '"recommendation":' in content.text:
                        return content.text
                elif content.type == "tool_use":
                    # Process tool call and get result
                    try:
                        result = await self._call_mcp_tool(content.name, content.input)
                            # Add tool call as a message
                        self.messages.append({
                            "role": "assistant",
                                "content": f"Using the credit_check tool with SSN {content.input['ssn']} and revenue ${content.input['business_revenue']:,.2f}..."
                        })
                            # Add tool result
                        self.messages.append({
                            "role": "user",
                            "content": result
                        })
                    except Exception as e:
                        # Add error result as user message
                        self.messages.append({
                            "role": "user",
                            "content": f"Error using tool: {str(e)}"
                        })

            # If we haven't returned yet, ask to continue
            if step < max_steps - 1:
                self.messages.append({
                    "role": "user",
                    "content": "Please continue your analysis and provide a final assessment in the requested JSON format."
                })

        return json.dumps({
            "risk_level": "error",
            "recommendation": "need_more_info",
            "reason": "Failed to complete assessment within maximum steps."
        }, indent=2)

    async def close(self):
        """Clean up resources."""
        await self.http_client.aclose()