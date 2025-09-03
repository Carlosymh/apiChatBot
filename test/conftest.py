# tests/conftest.py
import pytest
from dotenv import load_dotenv
import os

@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    """
    Fixture que se ejecuta una vez por sesión de prueba.
    Carga las variables de entorno del archivo para pruebas de integración
    antes de que se importe la app de FastAPI.
    """
    env_path = ".env.test.integration"
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path, override=True)
    else:
        print(f"Advertencia: El archivo de entorno '{env_path}' no fue encontrado.")