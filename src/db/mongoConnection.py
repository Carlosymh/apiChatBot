from pymongo import MongoClient

def get_mongo_client(MONGODB_URI: str) -> MongoClient:
    """
    Crea y devuelve un cliente de MongoDB.

    Args:
        mongodb_uri (str): La URI de conexión a MongoDB.

    Returns:
        MongoClient: Una instancia del cliente de MongoDB.
    """
    mongodb_client = MongoClient(MONGODB_URI)
    try:
        mongodb_client.admin.command("ping")
        print("Conexión a MongoDB exitosa.")
        return mongodb_client
    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")
        return None