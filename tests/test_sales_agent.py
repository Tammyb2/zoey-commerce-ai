import pytest

from app.agents.sales_agent import run_sales_agent


@pytest.mark.asyncio
async def test_run_sales_agent():
    result = await run_sales_agent(
        customer_phone="+2348012345678",
        message="Hello",
    )

    assert "response" in result
    assert "intent" in result
    assert isinstance(result["response"], str)
    assert isinstance(result["intent"], str)