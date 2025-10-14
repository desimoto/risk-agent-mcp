# Risk-Agent-MCP: AI-Powered Risk Assessment for Loan Underwriting

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

A Python-based Risk Agent leveraging Anthropic's Model Context Protocol (MCP) for secure integration with external tools like credit APIs. This agent assesses small business loan applications by reasoning over data, fetching credit scores, and flagging risks—ideal for financial services prototypes.

Inspired by MCP's open standard for tool chaining, it uses the beeAI framework for ReAct-style autonomy. Handles edge cases like "spotty financials in hot sectors" with adaptive queries.

## Features
- **MCP-Enabled Tooling**: Registers a `credit_check` tool server for secure API calls (e.g., Experian proxy).
- **Claude Integration**: Uses Anthropic's Claude 3.5 Sonnet for reasoning.
- **Stateful Memory**: Persists context across assessments via TokenMemory.
- **Modular Design**: Easy to extend with more agents (e.g., Compliance Agent).

## Quick Start
1. Clone the repo: `git clone https://github.com/yourusername/risk-agent-mcp.git`
2. Install deps: `pip install -r requirements.txt`
3. Set up env: `cp .env.example .env` and add your keys (ANTHROPIC_API_KEY, CREDIT_API_KEY).
4. Run example: `python examples/run_assessment.py`

Output example:
Risk Assessment: Score 720, low risk—proceed to compliance check.


## Architecture
- **risk_agent.py**: Core ReAct agent with MCP tool discovery.
- **mcp_credit_server.py**: Standalone MCP server for the credit tool.
- Flow: Orchestrator → Risk Agent → MCP Call → API → Enriched Reasoning.

## Setup for Dev
- Requires Python 3.10+.
- For MCP server: Run `python src/mcp_credit_server.py` in a subprocess (handled in agent).
- Testing: `pip install pytest` (already in reqs), `pytest tests/`.

## Contributing
Fork, PR with tests. See [CONTRIBUTING.md](CONTRIBUTING.md) if added.

## License
MIT. See [LICENSE](LICENSE).

Built for agentic FSI. Questions? Open an issue.
