import pytest

import app.tasks.tasks as tasks_module


def test_process_whatsapp_message_success(monkeypatch):
    """A valid message should be processed and saved."""

    history = [
        {"role": "customer", "content": "Hello"}
    ]
    saved = {}

    def fake_get_conversation(customer_phone):
        assert customer_phone == "2348012345678"
        return history.copy()

    def fake_run_sales_agent_sync(
        customer_phone,
        message,
        conversation_history,
    ):
        assert customer_phone == "2348012345678"
        assert message == "I need a phone"
        assert conversation_history == history.copy()

        return {
            "response": "What type of phone are you looking for?",
            "intent": "product_inquiry",
        }

    def fake_save_conversation(customer_phone, conversation):
        saved["customer_phone"] = customer_phone
        saved["conversation"] = conversation.copy()

    monkeypatch.setattr(
        tasks_module, "get_conversation", fake_get_conversation
    )
    monkeypatch.setattr(
        tasks_module, "run_sales_agent_sync",
        fake_run_sales_agent_sync,
    )
    monkeypatch.setattr(
        tasks_module, "save_conversation",
        fake_save_conversation,
    )

    result = tasks_module.process_whatsapp_message(
        {"customer_phone": "2348012345678",
         "message": "I need a phone"})  

    assert result["status"] == "processed"
    assert result["customer_phone"] == "2348012345678"
    assert result["intent"] == "product_inquiry"
    assert result["response"] == (
        "What type of phone are you looking for?"
    )

    assert saved["customer_phone"] == "2348012345678"
    assert saved["conversation"] == [
        {"role": "customer", "content": "Hello"},
        {"role": "customer", "content": "I need a phone"},
        {
            "role": "assistant",
            "content": "What type of phone are you looking for?",
        },
    ]


@pytest.mark.parametrize(
    ("payload", "expected_message"),
    [
        (
            {"message": "Hello"},
            "customer_phone is required",
        ),
        (
            {"customer_phone": "2348012345678"},
            "message is required",
        ),
        (
            {},
            "customer_phone is required",
        ),
    ],
)
def test_process_whatsapp_message_invalid_payload(
    payload,
    expected_message,
):
    """Invalid input should fail immediately without retries."""

    with pytest.raises(ValueError, match=expected_message):
        tasks_module.process_whatsapp_message(payload)


def test_process_whatsapp_message_agent_failure_does_not_save(
    monkeypatch,
):
    """A failed Sales Agent run must not save incomplete history."""

    history = [
        {"role": "customer", "content": "Previous message"}
    ]
    save_calls = []

    monkeypatch.setattr(
        tasks_module,
        "get_conversation",
        lambda customer_phone: history.copy(),
    )
    monkeypatch.setattr(
        tasks_module,
        "run_sales_agent_sync",
        lambda **kwargs: (_ for _ in ()).throw(
            RuntimeError("Sales Agent failed")
        ),
    )
    monkeypatch.setattr(
        tasks_module,
        "save_conversation",
        lambda *args, **kwargs: save_calls.append(args),
    )

    with pytest.raises(RuntimeError, match="Sales Agent failed"):
        tasks_module.process_whatsapp_message(
            {
                "customer_phone": "2348012345678",
                "message": "Find me a phone",
            }
        )

    assert save_calls == []