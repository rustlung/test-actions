## FastAPI: тестовый бэкенд времени

Эндпоинт `GET /time` возвращает текущее время сервера.

### Установка

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Запуск

```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Проверка

- `GET /time` — текущее время
- `GET /health` — простой healthcheck
- Swagger UI: `GET /docs`

Пример ответа `GET /time`:

```json
{
  "iso": "2025-12-28T14:03:12.123+03:00",
  "epoch_ms": 1766926992123,
  "tz": "Russian Standard Time"
}
```


