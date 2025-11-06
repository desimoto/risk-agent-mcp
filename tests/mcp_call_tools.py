import asyncio
from fastmcp import Client

client = Client("http://localhost:8000/mcp")

async def call_tool(input_data: dict):
    async with client:

        result = await client.call_tool("credit_check", {"input_data": input_data})

        if not result.is_error and result.structured_content:
            credit_data = result.structured_content
            
            score = credit_data['credit_score']
            risk = credit_data['risk_level']
            limit = credit_data['approved_limit']
            notes = credit_data['notes']
                        # Use the data as needed
            print(f"\n📊 Credit Check Results:")
            print(f"   Credit Score: {score}")
            print(f"   Risk Level: {risk}")
            print(f"   Approved Limit: ${limit:,.2f}")
            print(f"   Notes: {notes}")
        elif result.is_error:
            print("❌ Error occurred during tool call")
            if result.content:
                print(f"Error details: {result.content[0].text}")
        else:
            print("⚠️  No structured content available")

            
args = {"ssn": "999999999", "business_revenue": 1000000.50}
asyncio.run(call_tool(args))
