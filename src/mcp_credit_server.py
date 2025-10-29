"""
Standalone MCP server for credit check tool.
Now uses real Experian API for FICO score via owner's SSN (for small business personal guarantees).
Run with: python mcp_credit_server.py [stdio | http]
"""

import json
import os
import random
import sys
from typing import Dict, Any

import urllib.request
import urllib.error
from pydantic import BaseModel, Field

# Load .env for Experian creds
from dotenv import load_dotenv
load_dotenv()

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Credit Check Server", stateless_http=True)

class CreditCheckInput(BaseModel):
    """Input for credit check."""
    ssn: str = Field(..., description="Applicant's Social Security Number (owner's SSN for small business)")
    business_revenue: float = Field(..., description="Annual business revenue")

class CreditCheckOutput(BaseModel):
    """Output from credit check."""
    credit_score: int = Field(..., description="FICO score (300-850) from Experian")
    risk_level: str = Field(..., description="Risk level: low/medium/high")
    approved_limit: float = Field(..., description="Suggested loan limit")
    notes: str = Field(..., description="Risk notes, e.g., from API response")

def get_experian_token() -> str:
    """Fetch OAuth2 Bearer token from Experian sandbox."""
    url = "https://sandbox-us-api.experian.com/oauth2/v1/token"
    creds = {
        "username": os.getenv("EXPERIAN_USERNAME"),
        "password": os.getenv("EXPERIAN_PASSWORD"),
        "client_id": os.getenv("EXPERIAN_CLIENT_ID"),
        "client_secret": os.getenv("EXPERIAN_CLIENT_SECRET"),
        "grant_type": "password"
    }
    if not all(creds.values()):
        raise ValueError("Missing Experian env vars: EXPERIAN_USERNAME, PASSWORD, CLIENT_ID, CLIENT_SECRET")
    
    data = json.dumps(creds).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            tok_data = json.loads(response.read().decode('utf-8'))
            return tok_data["access_token"]
    except urllib.error.HTTPError as e:
        raise ValueError(f"Token fetch HTTP error: {e.code} - {e.read().decode()}")
    except Exception as e:
        raise ValueError(f"Token fetch failed: {e}")

@mcp.tool()
def credit_check(input_data: CreditCheckInput) -> CreditCheckOutput:
    """
    Securely fetch credit score from Experian API for small business loan applicant.
    Uses owner's SSN for FICO score (blended for small biz context).
    """
    print(type(input_data))
    try:
        token = get_experian_token()
        api_url = "https://sandbox-us-api.experian.com/consumerservices/credit-profile/v2/credit-report"
        body = {os.getenv("CREDIT_JSON_REQUEST")}
        data = json.dumps(body).encode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        req = urllib.request.Request(api_url, data=data, headers=headers, method='POST')
        
        with urllib.request.urlopen(req) as response:
            api_data = json.loads(response.read().decode('utf-8'))
            score = api_data.get("score", 500)  # Fallback if key missing
            api_notes = api_data.get("notes", "")
    except Exception as e:
        score = 500  # Neutral fallback
        api_notes = f"API call failed (check creds/endpoint): {str(e)}"
    
    revenue = input_data.business_revenue
    if revenue < 50000:
        risk = "high"
        notes = f"{api_notes} Low revenue; high default risk."
        limit = 0.0
    elif score < 600:
        risk = "high"
        notes = f"{api_notes} Spotty financials; consider sector volatility (e.g., hot sectors like tech may need extra scrutiny). Score: {score}"
        limit = revenue * 0.1
    elif score < 700:
        risk = "medium"
        notes = f"{api_notes} Fair credit; monitor cash flow. Score: {score}"
        limit = revenue * 0.3
    else:
        risk = "low"
        notes = f"{api_notes} Strong profile; approve with standard terms. Score: {score}"
        limit = revenue * 0.5
    
    return CreditCheckOutput(
        credit_score=score,
        risk_level=risk,
        approved_limit=limit,
        notes=notes
    )

@mcp.resource("credit://schema")
def get_credit_schema() -> Dict[str, Any]:
    """Schema for credit assessment context."""
    return {
        "version": "1.0",
        "fields": ["ssn", "revenue", "sector"],
        "risk_factors": ["low_score", "volatile_sector"]
    }

if __name__ == "__main__":
    transport = "streamable-http"  # Default for remote
    if len(sys.argv) > 1 and sys.argv[1] == "stdio":
        transport = "stdio"
    mcp.run(transport=transport)