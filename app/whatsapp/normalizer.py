from typing import Any, TypedDict


class NormalizedWhatsAppMessage(TypedDict):
    customer_phone: str
    customer_name: str | None
    message: str
    message_id: str


def normalize_whatsapp_webhook(
    payload: dict[str, Any],
) -> list[NormalizedWhatsAppMessage]:
    """
    Convert a Meta WhatsApp webhook payload into Zoey's
    internal message format.

    Returns an empty list when the webhook does not contain
    any supported customer text messages.
    """

    entries = payload.get("entry")

    if not isinstance(entries, list):
        return []

    normalized_messages: list[NormalizedWhatsAppMessage] = []

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        changes = entry.get("changes")

        if not isinstance(changes, list):
            continue

        for change in changes:
            if not isinstance(change, dict):
                continue

            if change.get("field") != "messages":
                continue

            value = change.get("value")

            if not isinstance(value, dict):
                continue

            customer_name: str | None = None

            contacts = value.get("contacts")

            if isinstance(contacts, list) and contacts:
                first_contact = contacts[0]

                if isinstance(first_contact, dict):
                    profile = first_contact.get("profile")

                    if isinstance(profile, dict):
                        name = profile.get("name")

                        if isinstance(name, str):
                            customer_name = name.strip() or None

            messages = value.get("messages")

            if not isinstance(messages, list):
                continue

            for message in messages:
                if not isinstance(message, dict):
                    continue

                if message.get("type") != "text":
                    continue

                sender = message.get("from")

                if not isinstance(sender, str) or not sender.strip():
                    continue

                message_id = message.get("id")

                if (
                    not isinstance(message_id, str)
                    or not message_id.strip()
                ):
                    continue

                text_data = message.get("text")

                if not isinstance(text_data, dict):
                    continue

                text_body = text_data.get("body")

                if not isinstance(text_body, str):
                    continue

                text_body = text_body.strip()

                if not text_body:
                    continue

                normalized_messages.append(
                    {
                        "customer_phone": sender.strip(),
                        "customer_name": customer_name,
                        "message": text_body,
                        "message_id": message_id.strip(),
                    }
                )

    return normalized_messages