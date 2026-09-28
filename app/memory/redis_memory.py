import json

import redis

from app.utils.config import settings
from app.agents.state import ConversationMessage


redis_client = redis.Redis.from_url(
    settings.redis_url,
    decode_responses=True,
)


def get_conversation_key(
    customer_phone: str,
) -> str:

    return f"zoey:conversation:{customer_phone}"


def get_conversation(
    customer_phone: str,
) -> list[ConversationMessage]:

    key = get_conversation_key(
        customer_phone
    )

    value = redis_client.get(key)

    if not value:
        return []

    return json.loads(value)


def save_conversation(
    customer_phone: str,
    conversation: list[ConversationMessage],
) -> None:

    key = get_conversation_key(
        customer_phone
    )

    redis_client.set(
        key,
        json.dumps(conversation),
        ex=60 * 60 * 24 * 30,
    )