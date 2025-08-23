# ChatBot API con FastAPI

## Requisitos previos

Antes de comenzar, asegúrate de tener instalados en tu máquina:

- **Python 3.10+** (con `pip`)
- **Docker** y **Docker Compose**

Puedes verificar la instalación con:
```bash
python3 --version
docker --version
docker-compose --version
Si no tienes Docker instalado, consulta la guía oficial:
https://docs.docker.com/get-docker/

Variables de entorno
Crea un archivo .env en la raíz con el siguiente contenido:

env
Copiar
Editar
MONGODB_URI=mongodb://mongo:27017
SERVERLESS_URL=https://mi-funcion-serverless.com/endpoint
Ajusta los valores según tu entorno.

Comandos principales
El proyecto incluye un Makefile con los siguientes comandos:

make – Muestra la lista de comandos disponibles.

make install – Instala las dependencias locales (requiere Python y pip).

make test – Ejecuta las pruebas con pytest.

make run – Levanta la aplicación y MongoDB con Docker.

make down – Detiene los servicios en ejecución.

make clean – Detiene y elimina los contenedores, redes y volúmenes.

Ejecución rápida
bash
Copiar
Editar
# Instalar dependencias locales (opcional si usarás Docker)
make install

# Levantar la aplicación y MongoDB con Docker
make run

# Acceder a la API
http://http://127.0.0.1:8000/docs

# Ejecutar pruebas
make test

# Detener los servicios
make down

# Limpiar contenedores y volúmenes
make clean
Endpoints principales
GET / – Verifica que la API está activa.

POST /chatBot – Envía mensajes al chatbot.

WS /ws – Conexión WebSocket para comunicación en tiempo real.

Estructura del proyecto
css
Copiar
Editar
.
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
├── main.py
├── src/
│   ├── api/
│   │   └── endpoints.py
│   ├── db/
│   │   └── mongoConnection.py
│   ├── models/
│   │   └── messageModel.py
│   └── utils/
│       └── functions.py
└── tests/
    └── test_main.py