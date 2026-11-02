import httpx

from app.utils.config import settings


def send_whatsapp_text_message(
        recipient_phone: str,
        message: str
) -> str:
    """
    Send a text message through the Whatsapp Cloud API.

    Args:
        recipient_phone: Customer's phone number in international format,
                            without the '+' sign.
        message: Text content to send.

    Returns: 
    The WhatsApp message ID returned by Meta.


    Raises: 
        ValueError: If required inout or configuration is missing.
        httpx.HTTPStatusError: If Meta retuns an unsuccessful HTTP status.
        httpx.RequestError: If the HTTP fails.
        ValueError: If Meta's response does not contain a message ID.
    """

    # 1. Validate the input.
    if not recipient_phone or not recipient_phone.strip():
        raise ValueError("recipient_phone is required")

    if not message or not message.strip():
        raise ValueError("message is required")

    
    # 2. Retrieve credentials
    access_token = settings.meta_access_token.get_secret_value()
    phone_number_id = settings.meta_phone_number_id

    if not access_token:
        raise ValueError("WhatsApp access token is not configured")

    if not phone_number_id:
        raise ValueError("WhatsApp phone number ID is not configured")


    # 3. Construct the Meta API Endpoint
    url = (
        f"https://graph.facebook.com/"
        f"{settings.meta_graph_api_version}/"
        f"{phone_number_id}/messages"
    )


    # 4. Prepare authentication headers.
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


    # 5. Prepare the WhatsApp message.
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_phone.strip(),
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message.strip()
        },
    }


    # 6. Send the request
    with httpx.Client(
        timeout=settings.meta_request_timeout
    ) as client:

        response = client.post(
            url,
            headers=headers,
            json=payload,
        )

        response.raise_for_status()


    # 7. Extract META's message ID
    try:
        response_data = response.json()
        message_id = response_data["messages"][0]["id"]
    except (ValueError, KeyError, IndexError, TypeError):
        raise ValueError(
            "WhatsApp API returned an invalid message response"
        ) from None

    if not message_id:
        raise ValueError(
            "WhatsApp did not return a message ID"
        )

    return message_id