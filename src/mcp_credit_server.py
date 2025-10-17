from mcp.server import McpServer
import os
import requests

server = McpServer()

@server.tool(
    name="credit_check",
    description="Fetch credit score and flags for applicant",
    input_schema={
        "type": "object",
        "properties": {
            "applicant_id": {"type": "string"},
            "ssn": {"type": "string"}
        },
        "required": ["applicant_id", "ssn"]
    },
    output_schema={
        "type": "object",
        "properties": {
            "score": {"type": "integer"},
            "risk_flags": {"type": "array", "items": {"type": "string"}}
        }
    }
)
async def credit_check(applicant_id: str, ssn: str) -> dict:
    endpoint = os.getenv("EXPERIAN_ENDPOINT")
    api_key = os.getenv("CREDIT_API_KEY")
    json_request = os.getenv("CREDIT_JSON_REQUEST")
    resp = requests.post(
        endpoint,
        json=json_request,
        headers={"Authorization": f"Bearer {api_key}"}
    )
    resp.raise_for_status()
    data = resp.json()
    return {
        "score": data.get("score", 0),
        "risk_flags": data.get("flags", [])
    }

if __name__ == "__main__":
    server.run()
