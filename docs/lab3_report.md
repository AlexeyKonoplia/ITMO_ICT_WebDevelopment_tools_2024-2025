# Лабораторная работа 3. Docker, интеграция парсера и очереди

## Цель
Упаковать FastAPI‑приложение и парсер в Docker, развернуть их вместе с PostgreSQL через docker‑compose и подготовить интеграцию. Дополнительно — настройка очередей задач (Celery + Redis).

## Сервисы docker-compose
Файл `laboratory_work3/docker-compose.yaml`:

```yaml
services:
  postgres:
    image: postgres:15
    container_name: postgres_container_lab
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
      POSTGRES_DB: ${DB_NAME:-app_db}
      PGDATA: /data/postgres
    volumes:
      - postgres:/data/postgres
    ports:
      - "5436:5432"
    networks:
      - backend

  fastapi_app:
    build:
      context: ./app
      dockerfile: Dockerfile
    container_name: fastapi_app
    depends_on:
      - postgres
    env_file:
      - .env
    ports:
      - "8000:8000"
    networks:
      - backend

  parser_app:
    build:
      context: ./parser
    	dockerfile: Dockerfile
    container_name: parser_app
    depends_on:
      - postgres
    env_file:
      - .env
    ports:
      - "8001:8001"
    networks:
      - backend

volumes:
  postgres:

networks:
  backend:
```

## Структура приложений
- `laboratory_work3/app` — FastAPI API (эндпоинты пользователей, книг, жанров, обменов; модели и схемы; `requirements.txt`).
- `laboratory_work3/parser` — сервис парсера (модуль `common` с подключением к БД, моделями и функциями парсинга; приложения `parser_app.py`, `parser_service.py`).

## Интеграция FastAPI ⇄ Парсер
- HTTP-вызов парсера: FastAPI добавляет эндпоинт `/parse`, который отправляет запрос к `parser_app`.
- Результат парсинга сохраняется в БД (общая сеть `backend`, общий PostgreSQL).

## Подготовка к очередям (опционально)
- Добавить сервисы `redis` и `celery-worker` в `docker-compose.yaml`.
- Вынести задачу парсинга в Celery task (брокер — Redis), запускать из FastAPI.

## Команды
- Сборка и запуск: `docker compose up -d --build`
- Логи: `docker compose logs -f fastapi_app`
- Остановка: `docker compose down`

## Выводы
- Контейнеризация упрощает развертывание и повторяемость среды.
- Разделение на сервисы ускоряет разработку и тестирование.
- Очереди задач позволяют выполнять длительные операции асинхронно.
