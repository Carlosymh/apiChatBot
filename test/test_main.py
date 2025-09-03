# test_main.py (sin cambios)
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to the Chat Bot API" in response.text

def test_chatbot_integration():
    """
    Esta prueba ahora hará una llamada real a la API de OpenAI
    """
    response = client.post("/chatBot", json={"message": "Hola, ¿cómo estás?", "conversation_id": None})
    
    assert response.status_code == 200
    json_response = response.json()
    assert "conversation_id" in json_response
    assert len(json_response["message"][1]["content"]) > 0