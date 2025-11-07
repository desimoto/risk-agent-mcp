[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![anthropic](https://img.shields.io/badge/anthropic-v0.71.0-orange.svg)](https://pypi.org/project/anthropic/)
[![mcp](https://img.shields.io/badge/mcp-v1.16.0-green.svg)](https://pypi.org/project/mcp/)
[![pydantic](https://img.shields.io/badge/pydantic-v2.12.3-purple.svg)](https://pypi.org/project/pydantic/)
[![python-dotenv](https://img.shields.io/badge/python--dotenv-v1.1.1-yellow.svg)](https://pypi.org/project/python-dotenv/)
[![fastmcp](https://img.shields.io/badge/fastmcp-2.12.5-blue.svg)](https://pypi.org/project/fastmcp/2.12.5/)

# Risk Agent for Small Business Loan Assessments

A Python-based Risk Agent leveraging Anthropic's Model Context Protocol (MCP) for secure integration with external tools like Experian's credit API. This agent assesses small business loan applications by reasoning over data, fetching credit scores, and flagging risks—ideal for financial services prototypes.

Inspired by MCP's open standard for tool chaining, it uses the Llama Stack framework for Features (configurable for provider-agnostic inference).

## Features
- **MCP-Enabled Tooling**: Registers a credit_check tool server for secure API calls (e.g., Experian proxy).
- **Claude Integration**: Uses Anthropic's Claude 3.5 Sonnet for reasoning.
- **Stateful Memory**: Persists context across assessments via message history.
- **Modular Design**: Easy to extend with more agents (e.g., Compliance Agent).
- **Real API Integration**: Fetches actual FICO scores from Experian sandbox (requires signup).

## Architecture
- `risk_agent.py`: Core ReAct agent with MCP tool discovery.
- `mcp_credit_server.py`: Standalone MCP server for the credit tool.
- Flow: Orchestrator → Risk Agent → MCP Call → API → Enriched Reasoning.
- ReAct-style autonomy. Handles edge cases like "spotty financials in hot sectors" with adaptive queries.

## Prerequisites
- Python 3.9+.
- Create `.env` from `.env.example` and fill in keys:
  - Anthropic API key: Sign up at [anthropic.com](https://anthropic.com) and set `ANTHROPIC_API_KEY`.
  - Experian API access: 
    - Sign up at [developer.experian.com](https://developer.experian.com) and create an app for Consumer Services (for FICO scores).
    - Get `CLIENT_ID` and `CLIENT_SECRET` from your app.
    - Use your Developer Portal `USERNAME` and `PASSWORD`.
    - Set in `.env`: `EXPERIAN_USERNAME`, `EXPERIAN_PASSWORD`, `EXPERIAN_CLIENT_ID`, `EXPERIAN_CLIENT_SECRET`.
- For production: Comply with FCRA (obtain consent for credit pulls). Use prod URLs and handle token caching. Override `.env` with actual env vars.

## Installation
1. Clone the repo: `git clone <repo-url> && cd risk-agent`.
2. cd risk-agent-mcp
3. Copy `.env.example` to `.env` and add your values.

## Option 1 - Create a python virtual environment
```bash
mkdir ~/.venv
python 3.12 -m venv ~/.venv/risk
source ~/.venv/risk/bin/activate
pip install -r requirements.txt
```

## Option 2 - Install [uv](https://docs.astral.sh/uv/getting-started/installation/) to create a python virtual environment
```bash
uv sync
```

```console
Resolved 75 packages in 3ms
Audited 69 packages in 2ms
```

## Running the Project
1. **Start the MCP Server** (in one terminal):  
   `python src/mcp_credit_server.py` or `uv run src/mcp_credit_server.py`  
   (Loads `.env` automatically; or `python mcp_credit_server.py stdio` for local testing.) 

Example output
```console
2025-11-05 11:45:24,816 - __main__ - INFO - Starting MCP Credit Server...
2025-11-05 11:45:24,816 - __main__ - INFO - Using transport mode: sse
2025-11-05 11:45:24,816 - __main__ - INFO - Log level: INFO
INFO:     Started server process [4225]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

2. **Run the Agent** (in another terminal):  
```bash
   cd src
   python main.py 
``` 
OR
```
uv run src/main.py
```

   (Loads `.env` automatically.)
   - This initializes the agent, discovers tools, and assesses a sample application.  
   - Output: Risk assessment JSON with score, level, and notes from Experian.

3. **Test with Custom Data**: Edit `main.py` sample_app dict (e.g., use test SSN from Experian docs like "000-00-0000" for sandbox).

## Example Client Output
```
2025-11-05 11:48:37,765 - root - INFO - Processing loan application with integrated FastMCP tools...
2025-11-05 11:48:40,318 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-11-05 11:48:40,336 - mcp_credit_server - INFO - Requesting token from Experian...
2025-11-05 11:48:42,749 - mcp_credit_server - INFO - Experian token obtained successfully.
2025-11-05 11:48:44,582 - root - INFO - Experian Credit Check Result: {'credit_score': 500, 'risk_level': 'high', 'approved_limit': '$7,500.00', 'notes': ' Spotty financials; consider sector volatility (e.g., hot sectors like tech may need extra scrutiny). Score: 500'}
2025-11-05 11:48:50,125 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"

Based on the credit check results and comprehensive analysis of the loan application, here is my final assessment:

**LOAN APPLICATION ASSESSMENT - TECH STARTUP INC.**

This application presents **SIGNIFICANT RISK** and should be **DECLINED** in its current form. The applicant has a credit score of 500, which falls into the high-risk category, and the approved credit limit of only $7,500.00 is substantially below the requested loan amount of $50,000.00. While the business shows annual revenue of $75,000.00, the loan request represents 66.7% of annual revenue, which is aggressive for a startup with poor credit fundamentals. The Technology sector adds additional risk due to inherent volatility and market sensitivity in this space. The credit check notes indicate "spotty financials," suggesting inconsistent payment history or financial management issues. The applicant's credit profile does not support approval for the full $50,000.00 requested. **Recommendation: DECLINE** the $50,000.00 loan request. If the applicant wishes to proceed, consider offering a significantly reduced loan amount (maximum $7,500.00 aligned with approved limit) contingent upon: (1) improved credit score through demonstrated payment history, (2) additional collateral or personal guarantee, and (3) detailed business plan addressing sector-specific risks and revenue growth projections.

```json
{
  "business_name": "Tech Startup Inc.",
  "owner_ssn": "123-45-6789",
  "annual_revenue": "$75,000.00",
  "sector": "Technology",
  "loan_amount_requested": "$50,000.00",
  "credit_score": 500,
  "risk_level": "high",
  "approved_limit": "$7,500.00",
  "recommendation": "DECLINE",
  "loan_to_revenue_ratio": "66.7%",
  "key_concerns": ["Low credit score (500)", "High risk classification", "Spotty financials", "Sector volatility (Technology)", "Loan request exceeds approved limit by 567%"]
}
```

## Extending the Project
- **Add Tools**: Register new MCP servers (e.g., for compliance checks) and include in `risk_agent.py`.
- **Llama Stack Integration**: Install Llama Stack (`pip install llama-stack-client`), configure `remote::anthropic` provider, and swap `anthropic.Anthropic` with `LlamaStackClient` in `risk_agent.py`.
- **Production Deployment**: Deploy MCP server remotely (e.g., via Docker/AWS). Cache Experian tokens. Add logging/error handling.

## Dependencies
Pinned for reproducibility (as of Oct 20, 2025):  
- `anthropic==0.71.0`  
- `mcp==1.16.0`  
- `pydantic==2.12.3`  
- `python-dotenv==1.1.1`
- `fastmcp==2.12.5`

## Troubleshooting
- **API Errors**: Check env vars; sandbox may require test data. Fallback to score 500 if creds invalid.
- **MCP Issues**: Ensure `mcp[cli]` installed; restart server if tools not discovered.
- **No Experian Access?**: Comment out API calls in `mcp_credit_server.py` and revert to random simulation for demo.

### MCP client test tools
```bash
uv run tests/mcp_list_tools.py
```
```console
Tool: credit_check
Description:
    Securely fetch credit score from Experian API for small business loan applicant.
    Uses owner's SSN for FICO score (blended for small biz context).

Parameters: {'$defs': {'CreditCheckInput': {'description': 'Input for credit check.', 'properties': {'ssn': {'description': "Applicant's Social Security Number (owner's SSN for small business)", 'title': 'Ssn', 'type': 'string'}, 'business_revenue': {'description': 'Annual business revenue', 'title': 'Business Revenue', 'type': 'number'}}, 'required': ['ssn', 'business_revenue'], 'title': 'CreditCheckInput', 'type': 'object'}}, 'properties': {'input_data': {'$ref': '#/$defs/CreditCheckInput'}}, 'required': ['input_data'], 'title': 'credit_checkArguments', 'type': 'object'}
```

```bash
uv run tests/mcp_call_tools.py
```
```console
📊 Credit Check Results:
   Credit Score: 500
   Risk Level: high
   Approved Limit: $100,000.05
   Notes:  Spotty financials; consider sector volatility (e.g., hot sectors like tech may need extra scrutiny). Score: 500
```

### MCP Inspector
```bash
npx @modelcontextprotocol/inspector --cli --method tools/list http://localhost:8000/mcp
```
```json
{
  "tools": [
    {
      "name": "credit_check",
      "description": "\nSecurely fetch credit score from Experian API for small business loan applicant.\nUses owner's SSN for FICO score (blended for small biz context).\n",
      "inputSchema": {
        "type": "object",
        "properties": {
          "input_data": {
            "$ref": "#/$defs/CreditCheckInput"
          }
        },
        "required": [
          "input_data"
        ],
        "$defs": {
          "CreditCheckInput": {
            "description": "Input for credit check.",
            "properties": {
              "ssn": {
                "description": "Applicant's Social Security Number (owner's SSN for small business)",
                "title": "Ssn",
                "type": "string"
              },
              "business_revenue": {
                "description": "Annual business revenue",
                "title": "Business Revenue",
                "type": "number"
              }
            },
            "required": [
              "ssn",
              "business_revenue"
            ],
            "title": "CreditCheckInput",
            "type": "object"
          }
        },
        "title": "credit_checkArguments"
      },
      "outputSchema": {
        "type": "object",
        "properties": {
          "credit_score": {
            "description": "FICO score (300-850) from Experian",
            "title": "Credit Score",
            "type": "integer"
          },
          "risk_level": {
            "description": "Risk level: low/medium/high",
            "title": "Risk Level",
            "type": "string"
          },
          "approved_limit": {
            "description": "Suggested loan limit",
            "title": "Approved Limit",
            "type": "number"
          },
          "notes": {
            "description": "Risk notes, e.g., from API response",
            "title": "Notes",
            "type": "string"
          }
        },
        "required": [
          "credit_score",
          "risk_level",
          "approved_limit",
          "notes"
        ],
        "description": "Output from credit check.",
        "title": "CreditCheckOutput"
      }
    }
  ]
}
```

```bash
npx @modelcontextprotocol/inspector --cli --method tools/call --tool-name=credit_check --tool-arg=input_data='{"ssn":"123-45-6789","business_revenue":123455}' http://127.0.0.1:8000/mcp
```

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\n  \"credit_score\": 500,\n  \"risk_level\": \"high\",\n  \"approved_limit\": 12345.5,\n  \"notes\": \" Spotty financials; consider sector volatility (e.g., hot sectors like tech may need extra scrutiny). Score: 500\"\n}"
    }
  ],
  "structuredContent": {
    "credit_score": 500,
    "risk_level": "high",
    "approved_limit": 12345.5,
    "notes": " Spotty financials; consider sector volatility (e.g., hot sectors like tech may need extra scrutiny). Score: 500"
  },
  "isError": false
}
```

For issues, see [Anthropic Docs](https://docs.anthropic.com) or [MCP Repo](https://github.com/anthropic/mcp).

## Contributing
Fork, PR with tests. See [CONTRIBUTING.md](CONTRIBUTING.md) if added.

## License
MIT. See [LICENSE](LICENSE).

Built for agentic FSI. Questions? Open an issue.
