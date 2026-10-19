
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_webhook_normalizes_and_queues_text_message():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WABA_ID",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "contacts": [
                                {
                                    "profile": {"name": "Boma"},
                                    "wa_id": "2348012345678",
                                }
                            ],
                            "messages": [
                                {
                                    "from": "2348012345678",
                                    "id": "wamid.TEST123",
                                    "type": "text",
                                    "text": {"body": "Hello Zoey"},
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }

    expected_message = {
        "customer_phone": "2348012345678",
        "customer_name": "Boma",
        "message": "Hello Zoey",
        "message_id": "wamid.TEST123",
    }

    with patch(
        "app.api.webhook.process_whatsapp_message.delay"
    ) as mock_delay:
        response = client.post("/webhook", json=payload)

    assert response.status_code == 200
    assert response.json() == {"status": "accepted"}
    mock_delay.assert_called_once_with(expected_message)


def test_webhook_ignores_invalid_payload():
    payload = {"object": "something_else"}

    with patch(
        "app.api.webhook.process_whatsapp_message.delay"
    ) as mock_delay:
        response = client.post("/webhook", json=payload)

    assert response.status_code == 200
    assert response.json() == {"status": "accepted"}
    mock_delay.assert_not_called()


def test_webhook_queues_each_text_message():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messages": [
                                {
                                    "from": "2348012345678",
                                    "id": "wamid.TEST1",
                                    "type": "text",
                                    "text": {"body": "Hello Zoey"},
                                },
                                {
                                    "from": "2348098765432",
                                    "id": "wamid.TEST2",
                                    "type": "text",
                                    "text": {"body": "I need help"},
                                },
                            ]
                        },
                    }
                ]
            }
        ],
    }

    with patch(
        "app.api.webhook.process_whatsapp_message.delay"
    ) as mock_delay:
        response = client.post("/webhook", json=payload)

    assert response.status_code == 200
    assert response.json() == {"status": "accepted"}

    assert mock_delay.call_count == 2
    mock_delay.assert_any_call(
        {
            "customer_phone": "2348012345678",
            "customer_name": None,
            "message": "Hello Zoey",
            "message_id": "wamid.TEST1",
        }
    )
    mock_delay.assert_any_call(
        {
            "customer_phone": "2348098765432",
            "customer_name": None,
            "message": "I need help",
            "message_id": "wamid.TEST2",
        }
    )
