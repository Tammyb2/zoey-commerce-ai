
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest

import app.services.whatsapp as whatsapp_module


@pytest.fixture
def fake_settings(monkeypatch):
    """Provide test credentials without using real Meta credentials."""

    test_settings = SimpleNamespace(
        meta_access_token=SimpleNamespace(
            get_secret_value=lambda: "test-access-token"
        ),
        meta_phone_number_id="123456789012345",
        meta_graph_api_version="v26.0",
        meta_request_timeout=15.0,
    )

    monkeypatch.setattr(
        whatsapp_module,
        "settings",
        test_settings,
    )

    return test_settings


def test_send_whatsapp_text_message_success(
    monkeypatch,
    fake_settings,
):
    """A successful API response should return the message ID."""

    expected_message_id = "wamid.test-message-123"

    mock_response = Mock()
    mock_response.json.return_value = {
        "messaging_product": "whatsapp",
        "messages": [
            {"id": expected_message_id}
        ],
    }

    mock_client = Mock()
    mock_client.post.return_value = mock_response

    class FakeClient:
        def __init__(self, **kwargs):
            assert kwargs["timeout"] == 15.0

        def __enter__(self):
            return mock_client

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(
        whatsapp_module.httpx,
        "Client",
        FakeClient,
    )

    result = whatsapp_module.send_whatsapp_text_message(
        recipient_phone="2348012345678",
        message="Hello from Zoey",
    )

    assert result == expected_message_id

    call_args = mock_client.post.call_args

    assert call_args.args[0] == (
        "https://graph.facebook.com/"
        "v26.0/123456789012345/messages"
    )

    assert call_args.kwargs["headers"] == {
        "Authorization": "Bearer test-access-token",
        "Content-Type": "application/json",
    }

    assert call_args.kwargs["json"] == {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": "2348012345678",
        "type": "text",
        "text": {
            "preview_url": False,
            "body": "Hello from Zoey",
        },
    }

    mock_response.raise_for_status.assert_called_once()


@pytest.mark.parametrize(
    ("recipient_phone", "message", "expected_error"),
    [
        ("", "Hello", "recipient_phone is required"),
        ("2348012345678", "", "message is required"),
        ("   ", "Hello", "recipient_phone is required"),
        ("2348012345678", "   ", "message is required"),
    ],
)
def test_send_whatsapp_text_message_invalid_input(
    recipient_phone,
    message,
    expected_error,
    fake_settings,
):
    """Empty recipient numbers and messages should be rejected."""

    with pytest.raises(ValueError, match=expected_error):
        whatsapp_module.send_whatsapp_text_message(
            recipient_phone=recipient_phone,
            message=message,
        )


def test_send_whatsapp_text_message_missing_access_token(
    monkeypatch,
    fake_settings,
):
    """Sending should fail when the access token is missing."""

    fake_settings.meta_access_token = SimpleNamespace(
        get_secret_value=lambda: ""
    )

    with pytest.raises(
        ValueError,
        match="WhatsApp access token is not configured",
    ):
        whatsapp_module.send_whatsapp_text_message(
            recipient_phone="2348012345678",
            message="Hello",
        )


def test_send_whatsapp_text_message_missing_phone_number_id(
    fake_settings,
):
    """Sending should fail when the phone number ID is missing."""

    fake_settings.meta_phone_number_id = ""

    with pytest.raises(
        ValueError,
        match="WhatsApp phone number ID is not configured",
    ):
        whatsapp_module.send_whatsapp_text_message(
            recipient_phone="2348012345678",
            message="Hello",
        )


def test_send_whatsapp_text_message_api_error(
    monkeypatch,
    fake_settings,
):
    """Meta HTTP errors should be propagated."""

    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.request = httpx.Request(
        "POST",
        "https://graph.facebook.com/test",
    )

    api_error = httpx.HTTPStatusError(
        "Bad Request",
        request=mock_response.request,
        response=mock_response,
    )

    mock_client = Mock()
    mock_client.post.side_effect = api_error

    class FakeClient:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            return mock_client

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(
        whatsapp_module.httpx,
        "Client",
        FakeClient,
    )

    with pytest.raises(httpx.HTTPStatusError):
        whatsapp_module.send_whatsapp_text_message(
            recipient_phone="2348012345678",
            message="Hello",
        )


def test_send_whatsapp_text_message_timeout(
    monkeypatch,
    fake_settings,
):
    """Network timeouts should be propagated."""

    mock_client = Mock()
    mock_client.post.side_effect = httpx.TimeoutException(
        "Request timed out"
    )

    class FakeClient:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            return mock_client

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(
        whatsapp_module.httpx,
        "Client",
        FakeClient,
    )

    with pytest.raises(httpx.TimeoutException):
        whatsapp_module.send_whatsapp_text_message(
            recipient_phone="2348012345678",
            message="Hello",
        )


@pytest.mark.parametrize(
    "response_body",
    [
        {},
        {"messages": []},
        {"messages": [{}]},
        {"messages": [{"id": ""}]},
        None,
    ],
)
def test_send_whatsapp_text_message_invalid_api_response(
    monkeypatch,
    fake_settings,
    response_body,
):
    """Malformed Meta responses should not be treated as success."""

    mock_response = Mock()
    mock_response.json.return_value = response_body

    mock_client = Mock()
    mock_client.post.return_value = mock_response

    class FakeClient:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            return mock_client

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(
        whatsapp_module.httpx,
        "Client",
        FakeClient,
    )

    with pytest.raises(ValueError):
        whatsapp_module.send_whatsapp_text_message(
            recipient_phone="2348012345678",
            message="Hello",
        )
