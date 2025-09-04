import requests
from typing import List
from ..db.mongoConnection import get_mongo_client
from datetime import datetime
import os
from dotenv import load_dotenv

from openai import OpenAI

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración de la base de datos y la API
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = "mongodb_genai_devday_rag"

client = OpenAI(
    api_key=os.environ.get("CLIENT_KEY")
)

def store_chat_message(conversation_id: str, role: str, content: str) -> None:
    """
    Almacena un mensaje de chat en la colección de historial de MongoDB.
    """
    message = {
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "timestamp": datetime.now(),
    }
    mongodb_client = get_mongo_client(MONGODB_URI)
    if not mongodb_client:
        return []
    history_collection = mongodb_client[DB_NAME]["chat_history"]
    history_collection.insert_one(message)
def retrieve_session_history(conversation_id: str) -> List:
    """
    Recupera el historial de mensajes de chat para una sesión específica.
    """
    mongodb_client = get_mongo_client(MONGODB_URI)
    if not mongodb_client:
        return []
    history_collection = mongodb_client[DB_NAME]["chat_history"]
    cursor = history_collection.find({"conversation_id": conversation_id}).sort("timestamp", 1).limit(10)
    
    if cursor:
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in cursor]
    else:
        messages = []
    
    return messages

def generate_answer_with_memory(conversation_id: str, user_query: str) -> dict:
    """
    Genera una respuesta a la consulta del usuario teniendo en cuenta el historial del chat.
    """
    messages = []
    system_message = {
        "role": "system", 
        "content": """Responde a la conversación basándote en la primera pregunta que haga el usuario. 
        Tus respuestas deben sonar como las de un humano que defiende su postura con respuestas persuasivas, sin ser demasiado argumentativo ni agresivo, 
        sin citar fuentes ni dar contexto externo.
        Si te pregunta algo que no tiene que ver con la conversación, responde y retoma el tema inicial de la conversación.
        Sé persuasivo sin explayarte."""
    }
    messages.append(system_message)

    message_history = retrieve_session_history(conversation_id)
    messages.extend(message_history)

    user_message = {"role": "user", "content": user_query}
    messages.append(user_message)

    response = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=messages
    )

    answer = response.choices[0].message.content

    store_chat_message(conversation_id, "user", user_query)
    store_chat_message(conversation_id, "assistant", answer)
    
    final_messages = message_history
    final_messages.append({"role": "user", "content": user_query})
    final_messages.append({"role": "assistant", "content": answer})
    
    return {"conversation_id": conversation_id, "message": final_messages}
