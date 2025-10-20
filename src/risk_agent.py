"""
Core ReAct agent for loan risk assessment.
Discovers MCP tools dynamically, uses Claude for reasoning.
Stateful via message history (TokenMemory equivalent).
Modular: Extend with more MCP servers/agents.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional

import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool

class RiskAgent:
    def __init__(self, api_key: str):
        self.anthropic_client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"  # Latest Claude 3.5 Sonnet
        self.messages: List[Dict[str, Any]] = []  # Stateful memory
        self.mcp_session: Optional[ClientSession] = None
        self.tools: List[Tool] = []

    async def initialize_mcp(self, server_script: str = "mcp_credit_server.py"):
        """Initialize MCP connection and discover tools."""
        server_params = StdioServerParameters(
            command="python",
            args=[server_script, "stdio"],
            env={},  # Add env vars if needed (e.g., API keys for real credit API)
            cwd="."
        )
        read, write = await stdio_client(server_params).__aenter__()
        self.mcp_session = ClientSession(read, write)
        await self.mcp_session.initialize()
        tools_resp = await self.mcp_session.list_tools()
        self.tools = tools_resp.tools
        print(f"Discovered {len(self.tools)} MCP tools.")

    def _tools_to_schemas(self) -> List[Dict[str, Any]]:
        """Convert MCP tools to Anthropic-compatible tool schemas."""
        schemas = []
        for tool in self.tools:
            schema = {
                "type": "function",
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": tool.inputSchema  # JSON schema from MCP
            }
            schemas.append(schema)
        return schemas

    async def _call_mcp_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Call tool via MCP and return observation."""
        if not self.mcp_session:
            raise ValueError("MCP not initialized.")
        result = await self.mcp_session.call_tool(name, arguments=arguments)
        # Extract text from structured/unstructured result
        if result.structuredContent:
            obs = json.dumps(result.structuredContent)
        else:
            obs = "\n".join([c.text for c in result.content if hasattr(c, 'text') and c.text])
        return f"Tool result: {obs}"

    async def assess_loan(self, application_data: Dict[str, Any]) -> str:
        """ReAct loop: Reason, Act (call MCP tool), Observe, repeat until final."""
        self.messages = [{"role": "user", "content": f"Assess this small business loan application for risks:\n{json.dumps(application_data, indent=2)}"}]

        system_prompt = """
        You are a Risk Agent for small business loans. Use ReAct reasoning: 
        - Thought: Analyze data and decide next step.
        - Action: If needed, call 'credit_check' tool with SSN (use owner_ssn) and revenue (use annual_revenue).
        - Observation: Review tool output.
        Handle edge cases like spotty financials in hot sectors (e.g., crypto/tech) with adaptive queries—flag volatility.
        End with Final Answer: [JSON: {"risk_level": "low/medium/high", "recommendation": str, "reason": str}]
        """

        max_steps = 5  # Prevent infinite loops
        for step in range(max_steps):
            tools_schemas = self._tools_to_schemas()
            response = self.anthropic_client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.1,
                system=system_prompt,
                messages=self.messages,
                tools=tools_schemas if tools_schemas else None,
            )
            self.messages.append({"role": "assistant", "content": [c.model_dump() for c in response.content]})

            if response.stop_reason == "end_turn" and not response.tool_calls:
                # Check for final answer
                last_content = response.content[0].text if response.content else ""
                if "Final Answer" in last_content or step >= max_steps - 1:
                    return last_content
                self.messages.append({"role": "user", "content": "Continue reasoning."})
                continue

            if response.tool_calls:
                for tool_call in response.tool_calls:
                    obs = await self._call_mcp_tool(tool_call.name, tool_call.input)
                    self.messages.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": tool_call.id,
                            "content": obs
                        }]
                    })
            else:
                break

        return "Assessment complete: Review messages for details."

    async def close(self):
        """Cleanup MCP session."""
        if self.mcp_session:
            await self.mcp_session.aclose()