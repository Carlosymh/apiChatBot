from fastapi import APIRouter, status, WebSocket, WebSocketDisconnect
from typing import Dict, Any
from src.utils.functions import generate_answer_with_memory
from src.models.messageModel import ChatMessage
import uuid
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Acepta la conexión del cliente
    await websocket.accept()
    print("Cliente conectado")
    
    try:
        while True:
            # Espera a recibir un JSON del cliente
            received_data = await websocket.receive_json()
            
            # Extrae los "parámetros" del JSON
            conversation_id = received_data.get("conversation_id")
            if not conversation_id:
                conversation_id = uuid.uuid4().hex
            message = received_data.get("message")
            anwer=generate_answer_with_memory(conversation_id, message, True)
            
            # Envía el objeto JSON de vuelta al cliente
            await websocket.send_json(anwer)
            
    except WebSocketDisconnect:
        print("Cliente desconectado")
    except Exception as e:
        print(f"Error: {e}")


@router.post("/chatBot", status_code=status.HTTP_200_OK)
async def chat_bot_endpoint(body: ChatMessage) -> Dict[str, Any]:
    
    if not body.conversation_id:
        conversation_id = uuid.uuid4().hex
    else:
        conversation_id = body.conversation_id
    anwer=generate_answer_with_memory(conversation_id, body.message, False)
    return anwer

@router.get("/")
async def get():
    return " Welcome to the Chat Bot API! Use the /chatBot endpoint to interact with the bot."