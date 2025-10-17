import pytest
import asyncio
from src.risk_agent import run_risk_assessment

@pytest.mark.asyncio
async def test_risk_assessment():
    applicant = {"name": "Test Co", "ein": "99-9999999", "sector": "test"}
    result = await run_risk_assessment(applicant)
    assert isinstance(result, str)
    assert len(result) > 10  # Basic sanity
