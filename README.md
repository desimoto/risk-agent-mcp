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
2. Copy `.env.example` to `.env` and add your values.
3. Install dependencies: `pip install -r requirements.txt`.

## Running the Project
1. **Start the MCP Server** (in one terminal):  
   `python mcp_credit_server.py`  
   (Loads `.env` automatically; or `python mcp_credit_server.py stdio` for local testing.)

2. **Run the Agent** (in another terminal):  
   `python main.py`  
   (Loads `.env` automatically.)
   - This initializes the agent, discovers tools, and assesses a sample application.  
   - Output: Risk assessment JSON with score, level, and notes from Experian.

3. **Test with Custom Data**: Edit `main.py` sample_app dict (e.g., use test SSN from Experian docs like "000-00-0000" for sandbox).

## Example Output
```
Risk Assessment:
Final Answer: {"risk_level": "medium", "recommendation": "Proceed with caution; cap at 50% of revenue", "reason": "Score: 650 from Experian. Fair credit in tech sector—monitor volatility."}
```

## Extending the Project
- **Add Tools**: Register new MCP servers (e.g., for compliance checks) and include in `risk_agent.py`.
- **Llama Stack Integration**: Install Llama Stack (`pip install llama-stack-client`), configure `remote::anthropic` provider, and swap `anthropic.Anthropic` with `LlamaStackClient` in `risk_agent.py`.
- **Production Deployment**: Deploy MCP server remotely (e.g., via Docker/AWS). Cache Experian tokens. Add logging/error handling.

## Dependencies
Pinned for reproducibility (as of Oct 20, 2025):  
- `anthropic==0.71.0`  
- `mcp[cli]==1.18.0`  
- `pydantic==2.12.3`  
- `python-dotenv==1.0.1`

## Troubleshooting
- **API Errors**: Check env vars; sandbox may require test data. Fallback to score 500 if creds invalid.
- **MCP Issues**: Ensure `mcp[cli]` installed; restart server if tools not discovered.
- **No Experian Access?**: Comment out API calls in `mcp_credit_server.py` and revert to random simulation for demo.

For issues, see [Anthropic Docs](https://docs.anthropic.com) or [MCP Repo](https://github.com/anthropic/mcp).

## Contributing
Fork, PR with tests. See [CONTRIBUTING.md](CONTRIBUTING.md) if added.

## License
MIT. See [LICENSE](LICENSE).

Built for agentic FSI. Questions? Open an issue.
