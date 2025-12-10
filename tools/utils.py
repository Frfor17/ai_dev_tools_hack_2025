"""Общие утилиты для CAD инструментов."""

import httpx
from typing import Dict, Any, Optional
from mcp.types import TextContent

# URL вашего FastAPI сервера (можно вынести в переменные окружения)
FASTAPI_URL = "http://localhost:8000"

# Асинхронный HTTP клиент (с общим для всех запросов)
_client = None

async def get_client():
    """Создаем или возвращаем HTTP клиент."""
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=30.0)
    return _client

class ToolResult:
    """Результат выполнения инструмента."""
    
    def __init__(
        self,
        content: list,
        structured_content: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.structured_content = structured_content or {}
        self.meta = meta or {}