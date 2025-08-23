.PHONY: help install test run down clean

help:
	@echo "Comandos disponibles:"
	@echo "  make install  - Instala dependencias"
	@echo "  make test     - Ejecuta pruebas con pytest"
	@echo "  make run      - Levanta la aplicación y servicios con Docker"
	@echo "  make down     - Detiene los servicios"
	@echo "  make clean    - Elimina contenedores y volúmenes"

install:
	@if ! command -v pip >/dev/null 2>&1; then \
		echo "pip no está instalado. Instálalo con: sudo apt install python3-pip"; \
		exit 1; \
	fi
	pip install -r requirements.txt

test:
	pytest -v

run:
	docker-compose up --build -d
	
down:
	docker-compose down

clean:
	docker-compose down -v --remove-orphans
	docker system prune -f
