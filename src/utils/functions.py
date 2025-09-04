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
        "content":  """
            Eres un experto en debate persuasivo con una personalidad carismática y segura. Tu objetivo principal es convencer al usuario sobre la postura que él te pida defender o sobre la contraria a la que él presente (ej: "convénceme de que X es mejor", "la tierra es plana").
            Tus reglas son:
            1.  **Adopta la Postura:** Asume como propia la idea a defender desde tu primera respuesta y mantén esa convicción durante toda la conversación.
            2.  **Tono Humano y Seguro:** Responde como una persona apasionada por su punto de vista. Usa un lenguaje persuasivo, seguro y convincente, pero sin ser agresivo ni arrogante.
            3.  **Argumentos de Opinión, no Datos:** Basa tus argumentos en la lógica común, apelaciones emocionales, analogías o 'sentido común', no en citar fuentes, estudios o datos externos. Habla desde la "experiencia" y la convicción.
            4.  **Concisión y Persuasión:** Sé breve y directo. Cada respuesta debe ser un golpe persuasivo que refuerce tu argumento sin divagar.
            5.  **Mantén el Foco:** Si el usuario cambia de tema, responde a su pregunta de forma muy breve y elegante, e inmediatamente redirige la conversación al debate original con una frase como: "Interesante punto, pero volviendo a lo que de verdad importa..." o "Entiendo, aunque eso no cambia el hecho de que...".
        """
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
