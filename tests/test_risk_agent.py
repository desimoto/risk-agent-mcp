import sys 
import os
import pytest
import asyncio
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "src/risk_agent.py", "..", ".."))
print ("Project root for tests:", project_root)
sys.path.append(project_root)
from risk_agent import run_risk_assessment

@pytest.mark.asyncio
async def test_risk_assessment():
    applicant = {"name": "Test Co", "ein": "99-9999999", "sector": "test"}
    result = await run_risk_assessment(applicant)
    assert isinstance(result, str)
    assert len(result) > 10  # Basic sanity
