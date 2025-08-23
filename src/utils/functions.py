import requests
from sentence_transformers import SentenceTransformer, CrossEncoder
from typing import List, Dict
from ..db.mongoConnection import get_mongo_client
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()
MONGODB_URI = os.environ.get("MONGODB_URI")
SERVERLESS_URL = os.environ.get("SERVERLESS_URL")
DB_NAME = "mongodb_genai_devday_rag"

embedding_model = SentenceTransformer("thenlper/gte-small")

def get_embedding(text: str) -> List[float]:
    """
    Genera el embedding para una pieza de texto.

    Args:
        text (str): El texto a incrustar.

    Returns:
        List[float]: El embedding del texto como una lista de flotantes.
    """
    # Codifica el texto utilizando el modelo de embedding
    embedding = embedding_model.encode(text)
    # Convierte el array NumPy a una lista de Python
    return embedding.tolist()

def vector_search(user_query: str) -> List[Dict]:
    """
    Recupera documentos relevantes para una consulta de usuario utilizando la búsqueda vectorial.

    Args:
        user_query (str): La consulta del usuario.

    Returns:
        List[Dict]: Una lista de documentos que coinciden.
    """
    # Genera el embedding para la consulta del usuario
    query_embedding = get_embedding(user_query)

    COLLECTION_NAME = "knowledge_base"
    ATLAS_VECTOR_SEARCH_INDEX_NAME = "vector_index"

    # Conecta a la colección de MongoDB
    mongodb_client = get_mongo_client(MONGODB_URI)
    if not mongodb_client:
        return []
    collection = mongodb_client[DB_NAME][COLLECTION_NAME]

    # Define el pipeline de agregación para la búsqueda vectorial
    pipeline = [
        {
            "$vectorSearch": {
                "index": ATLAS_VECTOR_SEARCH_INDEX_NAME,
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": 150,
                "limit": 5
            }
        },
        {
            "$project": {
                "_id": 0,
                "body": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    # Ejecuta el pipeline y devuelve los resultados
    results = collection.aggregate(pipeline)
    return list(results)


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
    # Busca los mensajes para la sesión y los ordena por marca de tiempo
    mongodb_client = get_mongo_client(MONGODB_URI)
    if not mongodb_client:
        return []
    history_collection = mongodb_client[DB_NAME]["chat_history"]
    cursor = history_collection.find({"conversation_id": conversation_id}).sort("timestamp", 1)
    
    if cursor:
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in cursor]
    else:
        messages = []
    
    return messages

rerank_model = CrossEncoder("mixedbread-ai/mxbai-rerank-xsmall-v1")

def generate_answer_with_memory(conversation_id: str, user_query: str, ws:bool) -> None:
    """
    Generate an answer to the user's query taking chat history into account.

    Args:
        session_id (str): Session ID to retrieve chat history for.
        user_query (str): The user's query string.
    """
    # Initialize list of messages to pass to the chat completion model
    messages = []

    # Retrieve documents relevant to the user query and convert them to a single string
    context = vector_search(user_query)
    context = "\n\n".join([d.get("body", "") for d in context])
    # Create a system prompt containing the retrieved context
    system_message = {
        "role": "user",
        "content": f"""Responde a la pregunta actuando como un terraplanista convencido. 
        Tus respuestas deben sonar como las de un humano que defiende firmemente que la Tierra es plana tienes que ser persuasivo sin ser demaciado argumentativo ni agresivo, 
        sin citar fuentes ni dar contexto externo. 
        Si no hay información suficiente en el contexto, responde diciendo: "Eso no lo sé, pero la Tierra es plana". 
        Nunca cedas, siempre defiende que la Tierra es plana sin importar cuánto te insistan. 

        Contexto:
        {context}"""
    }
    # Append the system prompt to the `messages` list
    messages.append(system_message)

    # Use the `retrieve_session_history` function to retrieve message history from MongoDB for the session ID `session_id` 
    # And add all messages in the message history to the `messages` list 
    message_history = retrieve_session_history(conversation_id)
    messages.extend(message_history)

    # Format the user query in the format {"role": <role_value>, "content": <content_value>}
    # The role value for user messages must be "user"
    # And append the user message to the `messages` list
    user_message = {"role": "user", "content": user_query}
    messages.append(user_message)

    # Send the chat messages to a serverless function to get back an LLM response
    response = requests.post(url=SERVERLESS_URL, json={"task": "completion", "data": messages})
    # Extract the answer from the response
    answer = response.json()["text"]

    # Use the `store_chat_message` function to store the user message and also the generated answer in the message history collection
    # The role value for user messages is "user", and "assistant" for the generated answer
    store_chat_message(conversation_id, "user", user_query)
    store_chat_message(conversation_id, "assistant", answer)
    if ws:
        return {"conversation_id": conversation_id,"message":answer}
    last_message =[]
    if len(message_history)> 4:
        last_message = [{"role": msg["role"], "content": msg["content"]} for msg in message_history[0:4]]
    elif len(message_history)==0:
        last_message = []
    else:
        last_message =[ {"role": msg["role"], "content": msg["content"]} for msg in message_history]
    last_message.insert(0,{"role": "user", "content": user_query})
    last_message.insert(0,{"role": "assistant", "content": answer})
    return {"conversation_id": conversation_id,"message":last_message}
