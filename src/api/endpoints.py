from fastapi import APIRouter, status
from typing import Dict, Any
from src.utils.functions import generate_answer_with_memory
from src.models.messageModel import ChatMessage
import uuid

router = APIRouter()



@router.post("/chatBot", status_code=status.HTTP_200_OK)
async def chat_bot_endpoint(body: ChatMessage) -> Dict[str, Any]:
    
    if not body.conversation_id:
        conversation_id = uuid.uuid4().hex
    else:
        conversation_id = body.conversation_id
    anwer=generate_answer_with_memory(conversation_id, body.message)
    return anwer

@router.get("/")
async def get():
    return " Welcome to the Chat Bot API! Use the /chatBot endpoint to interact with the bot."