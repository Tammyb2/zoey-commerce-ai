from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

def test_webhook():
    payload = {
        "test": True,
        "message": "Hello Zoey",
    }

    response = client.post(
        "/webhook",
        json=payload,
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "accepted"
    }