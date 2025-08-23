from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to the Chat Bot API" in response.text

def test_chatbot():
    response = client.post("/chatBot", json={"message": "Hola", "conversation_id": None})
    assert response.status_code == 200
    assert "conversation_id" in response.json()
