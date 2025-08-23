from pydantic import BaseModel
from typing import Optional

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None