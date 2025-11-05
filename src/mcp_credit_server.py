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
import logging
import urllib.request
import urllib.error
from pydantic import BaseModel, Field
import requests

def setup_logging(log_level=logging.INFO):
    """Configure logging to work properly with uvicorn."""
    # Create a custom formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get the root logger
    root_logger = logging.getLogger()
    
    # Remove any existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # Configure root logger
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # Configure uvicorn loggers to use our format
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_error = logging.getLogger("uvicorn.error")
    uvicorn_access.handlers = [console_handler]
    uvicorn_error.handlers = [console_handler]
    
    return logging.getLogger(__name__)

# Initialize logging
logger = setup_logging()

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
    url = os.getenv("EXPERIAN_TOKEN_ENDPOINT")
    creds = {
        "username": os.getenv("EXPERIAN_USERNAME"),
        "password": os.getenv("EXPERIAN_PASSWORD"),
        "client_id": os.getenv("EXPERIAN_CLIENT_ID"),
        "client_secret": os.getenv("EXPERIAN_CLIENT_SECRET"),
        "grant_type": "password"
    }
    if not all(creds.values()):
        raise ValueError("Missing Experian env vars: EXPERIAN_USERNAME, PASSWORD, CLIENT_ID, CLIENT_SECRET")

    logger.info("Requesting token from Experian...")
    headers = {"Content-Type": "application/x-www-form-urlencoded", 'Accept': 'application/json'}
    logger.debug("Token request being sent.")
    logger.debug(f"Request details: URL={url}, Headers={headers}")
    
    try:
        logger.debug(f"Token request headers: {headers}")
        # Don't log credentials for security
        logger.debug("Sending token request to Experian...")
        resp = requests.post(url, data=creds, headers=headers)
        logger.debug(f"Token response status: {resp.status_code}")
        
        if resp.status_code == 200:
            token_data = resp.json()
            logger.debug("Successfully obtained token from Experian")
            return token_data.get("access_token")
        else:
            logger.error(f"Token request failed with status {resp.status_code}: {resp.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error obtaining token: {e}")
        if hasattr(e, "response") and getattr(e, "response") is not None:
            logger.error(f"Token error details: {e.response.text}")
        return None

@mcp.tool()
def credit_check(input_data: CreditCheckInput) -> CreditCheckOutput:
    """
    Securely fetch credit score from Experian API for small business loan applicant.
    Uses owner's SSN for FICO score (blended for small biz context).
    """
    logger.debug("credit_check tool is running...")
    logger.debug(f"Input data received: {input_data}")
    try:
        token = get_experian_token()
        if not token:
            raise ValueError("Failed to obtain token from Experian")
        logger.info("Experian token obtained successfully.")
        
        api_url = os.getenv("EXPERIAN_CREDIT_ENDPOINT")
        if not api_url:
            raise ValueError("EXPERIAN_CREDIT_ENDPOINT not configured")
            
        # Create request body with actual input data
        # Clean up SSN (remove dashes)
        clean_ssn = input_data.ssn.replace("-", "").replace(" ", "")
        logger.debug(f"Cleaned SSN: {clean_ssn}")
        
        # body = {"consumerPii": { "primaryApplicant": { "name": { "lastName": "CANN", "firstName": "JOHN", "middleName": "N" }, "dob": { "dob": "1955" }, "ssn": { "ssn": "111111111" }, "currentAddress": { "line1": "510 MONDRE ST", "city": "MICHIGAN CITY", "state": "IN", "zipCode": "46360" } } }, "requestor": { "subscriberCode": "2222222" }, "permissiblePurpose": { "type": "08" }, "resellerInfo": { "endUserName": "CPAPIV2TC21" }, "vendorData": { "vendorNumber": "072", "vendorVersion": "V1.29" }, "addOns": { "directCheck": "", "demographics": "Only Phone", "clarityEarlyRiskScore": "Y", "liftPremium": "Y", "clarityData": { "clarityAccountId": "0000000", "clarityLocationId": "000000", "clarityControlFileName": "test_file", "clarityControlFileVersion": "0000000" }, "renterRiskScore": "N", "rentBureauData": { "primaryApplRentBureauFreezePin": "1234", "secondaryApplRentBureauFreezePin": "112233" }, "riskModels": { "modelIndicator": [ "" ], "scorePercentile": "" }, "summaries": { "summaryType": [ "" ] }, "fraudShield": "Y", "mla": "", "ofacmsg": "", "consumerIdentCheck": { "getUniqueConsumerIdentifier": "" }, "joint": "", "paymentHistory84": "", "syntheticId": "N", "taxRefundLoan": "Y", "sureProfile": "Y", "incomeAndEmploymentReport": "Y", "incomeAndEmploymentReportData": { "verifierName": "Experian", "reportType": "ExpVerify-Plus" } }, "customOptions": { "optionId": [ "COADEX" ] } }
        
        with open("data/income_employment.json", 'r', encoding='utf-8') as file:
            body = json.load(file)
            
        logger.debug(f'Request body: {json.dumps(body, indent=2)}')
        data = json.dumps(body).encode('utf-8')
        
        # Get company ID from environment or use default
        company_id = os.getenv("EXPERIAN_COMPANY_ID", "0000000")  # Default sandbox company ID
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
            'accept': 'application/json',
            'clientReferenceId':'SBMYSQL'
        }
        logger.debug(f"Making API call to {api_url} with company ID: {company_id}")
        
        req = urllib.request.Request(api_url, data=data, headers=headers, method='POST')
        
        with urllib.request.urlopen(req) as response:
            response_text = response.read().decode('utf-8')
            logger.debug(f"API response: {response_text}")
            api_data = json.loads(response_text)
            score = api_data.get("score", 500)  # Fallback if key missing
            api_notes = api_data.get("notes", "")
    except urllib.error.HTTPError as e:
        score = 500  # Neutral fallback
        error_body = e.read().decode('utf-8') if hasattr(e, 'read') else 'No error body'
        api_notes = f"API HTTP Error {e.code}: {error_body}"
        logger.error(f"Experian API HTTP Error: {e.code} - {error_body}")
    except Exception as e:
        score = 500  # Neutral fallback
        api_notes = f"API call failed: {str(e)}"
        logger.error(f"Experian API call failed: {str(e)}", exc_info=True)
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
    # Parse command line arguments
    transport = "streamable-http"  # Default for remote
    
    # Check for log level from environment variable first
    env_log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_level = getattr(logging, env_log_level, logging.INFO)
    
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg in ["stdio", "http", "sse"]:
            if arg == "stdio":
                transport = "stdio"
            elif arg == "http":
                transport = "streamable-http"
            elif arg == "sse":
                transport = "sse"
        elif arg.startswith("--log-level="):
            level_name = arg.split("=")[1].upper()
            log_level = getattr(logging, level_name, logging.INFO)
        elif arg in ["--debug"]:
            log_level = logging.DEBUG
        elif arg in ["--verbose", "-v"]:
            log_level = logging.DEBUG
        elif arg in ["--quiet", "-q"]:
            log_level = logging.WARNING
    
    # Ensure logging is properly configured with the specified level
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    logger.info("Starting MCP Credit Server...")
    logger.info(f"Using transport mode: {transport}")
    logger.info(f"Log level: {logging.getLevelName(log_level)}")
    
    mcp.run(transport=transport)
