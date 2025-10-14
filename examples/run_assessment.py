import asyncio
from src.risk_agent import run_risk_assessment

async def main():
    applicant = {
        "name": "GreenTech Startup",
        "ein": "12-3456789",
        "sector": "renewables",
        "ssn": "123-45-6789"  # Mock for demo
    }
    result = await run_risk_assessment(applicant)
    print(f"Risk Assessment: {result}")

if __name__ == "__main__":
    asyncio.run(main())
