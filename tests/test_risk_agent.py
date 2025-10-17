import sys
import os
import pytest
import asyncio
# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.risk_agent import run_risk_assessment

@pytest.mark.asyncio
async def test_risk_assessment():
    applicant = {"name": "Test Co", "ein": "99-9999999", "sector": "test"}
    result = await run_risk_assessment(applicant)
    assert isinstance(result, str)
    assert len(result) > 10  # Basic sanity
