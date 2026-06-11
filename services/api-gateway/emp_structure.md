api-gateway/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── dependencies.py   # проверка JWT
│   ├── proxy/
│   │   ├── __init__.py
│   │   └── client.py         # httpx проксирование
│   └── api/
│       ├── __init__.py
│       └── router.py         # все маршруты
├── .env
├── pyproject.toml
└── Dockerfile
