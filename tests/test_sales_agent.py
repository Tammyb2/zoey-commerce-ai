
from types import SimpleNamespace

import pytest

from app.agents.sales_agent import run_sales_agent


class FakeModel:
    def __init__(self):
        self.responses = [
            SimpleNamespace(content="greeting"),
            SimpleNamespace(
                content="Hello! 👋 How can I help you today?"
            ),
        ]

    async def ainvoke(self, prompt):
        return self.responses.pop(0)


@pytest.mark.asyncio
async def test_run_sales_agent(monkeypatch):
    fake_model = FakeModel()

    monkeypatch.setattr(
        "app.graph.nodes.get_chat_model",
        lambda: fake_model,
    )

    result = await run_sales_agent(
        customer_phone="+2348012345678",
        message="Hello",
    )

    assert result["intent"] == "greeting"
    assert result["response"] == "Hello! 👋 How can I help you today?"
