from app.whatsapp.normalizer import normalize_whatsapp_webhook



def test_normalize_text_message():
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
                                    "profile": {
                                        "name": "Boma",
                                    },
                                    "wa_id": "2348012345678",
                                }
                            ],
                            "messages": [
                                {
                                    "from": "2348012345678",
                                    "id": "wamid.TEST123",
                                    "type": "text",
                                    "text": {
                                        "body": "Hello Zoey",
                                    },
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }

    result = normalize_whatsapp_webhook(payload)

    assert result == [
        {
            "customer_phone": "2348012345678",
            "customer_name": "Boma",
            "message": "Hello Zoey",
            "message_id": "wamid.TEST123",
        }
    ]


def test_normalize_ignores_image_message():
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
                                    "id": "wamid.IMAGE123",
                                    "type": "image",
                                    "image": {"id": "IMAGE123"},
                                }
                            ]
                        },
                    }
                ]
            }
        ],
    }

    assert normalize_whatsapp_webhook(payload) == []


def test_normalize_invalid_webhook():
    payload = {"object": "something_else"}

    assert normalize_whatsapp_webhook(payload) == []


def test_normalize_multiple_messages():
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

    result = normalize_whatsapp_webhook(payload)

    assert len(result) == 2
    assert result[0]["message"] == "Hello Zoey"
    assert result[1]["message"] == "I need help"
