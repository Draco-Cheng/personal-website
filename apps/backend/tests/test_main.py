from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestPingEndpoint:
    def test_ping_returns_pong(self):
        """Test that /ping returns the expected response."""
        response = client.get("/ping")
        assert response.status_code == 200
        assert response.json() == {"result": "pong"}

    def test_ping_response_structure(self):
        """Test that /ping response has the correct structure."""
        response = client.get("/ping")
        data = response.json()
        assert "result" in data
        assert isinstance(data["result"], str)
        assert data["result"] == "pong"

class TestChatEndpoint:
    def test_chat_endpoint_structure(self):
        """Test that /chat accepts the correct request structure."""
        response = client.post(
            "/chat",
            json={"message": "Hello"}
        )
        # Should return 503 if OpenAI is not configured, or 200 if configured
        assert response.status_code in [200, 503]

    def test_chat_empty_message_returns_400(self):
        """Test that empty messages are rejected."""
        response = client.post(
            "/chat",
            json={"message": ""}
        )
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    def test_chat_response_structure_when_available(self):
        """Test chat response has correct structure when OpenAI is available."""
        response = client.post(
            "/chat",
            json={"message": "What is your experience?"}
        )
        if response.status_code == 200:
            data = response.json()
            assert "response" in data
            assert isinstance(data["response"], str)
