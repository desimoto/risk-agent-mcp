import asyncio
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from beeai_framework.agents.react.agent import ReActAgent
from beeai_framework.backend.chat import ChatModel
from beeai.framework.integrations.mcp import MCPTool
#from beeai_framework.tools.mcp_tools import MCPTool
from beeai_framework.adapters.anthropic.backend.chat import AnthropicChatModel
from beeai_framework.memory.token_memory import TokenMemory

load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

async def setup_risk_agent():
    credit_server_params = StdioServerParameters(
        command="python",
        args=["src/mcp_credit_server.py"],
        env={
            "CREDIT_API_KEY": os.getenv("CREDIT_API_KEY"),
            "EXPERIAN_ENDPOINT": os.getenv("EXPERIAN_ENDPOINT", "https://api.experian.com/v1/credit")
        }
    )

    async with stdio_client(credit_server_params) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        credit_tools = await MCPTool.from_client(session, credit_server_params)

    llm = AnthropicChatModel(
        model_id="claude-3-5-sonnet-20240620",
        api_key=ANTHROPIC_API_KEY
    )

    agent = ReActAgent(
        llm=llm,
        tools=credit_tools,
        memory=TokenMemory(llm)
    )

    await agent.memory.add("You are a Risk Agent for loan underwriting. Use credit_check to fetch scores, reason on flags (e.g., high debt), and suggest next steps like fraud huddle.")

    return agent

async def run_risk_assessment(applicant_context: dict):
    agent = await setup_risk_agent()
    
    prompt = f"""
    Assess risk for applicant: {applicant_context}.
    Pull credit via tool if needed, factor in green tech sector vibes.
    Output: Risk score summary and recommendation.
    """
    
    response = await agent.run(prompt=prompt)
    return response.result.text
