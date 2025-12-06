"""Общие утилиты для инструментов MCP."""
import os
from typing import Dict, Any, List
from dataclasses import dataclass
from mcp.types import TextContent
from mcp.shared.exceptions import McpError, ErrorData
import json

@dataclass
class ToolResult:
    """Результат выполнения инструмента."""
    content: List[TextContent]
    structured_content: Dict[str, Any] = None
    meta: Dict[str, Any] = None

def _require_env_vars(names: list[str]) -> dict[str, str]:
    """Проверяет наличие обязательных переменных окружения."""
    missing = [n for n in names if not os.getenv(n)]
    if missing:
        raise McpError(
            ErrorData(
                code=-32602,
                message="Отсутствуют обязательные переменные окружения: " + ", ".join(missing)
            )
        )
    return {n: os.getenv(n, "") for n in names}

def format_api_error(response_text: str, status_code: int) -> str:
    """Форматирует ошибку API в понятное сообщение."""
    try:
        error_data = json.loads(response_text)
        code = error_data.get("code", "unknown")
        message = error_data.get("message", response_text)
        error_msg = f"Ошибка API (код {code}): {message}"
        if status_code == 401:
            error_msg = "Ошибка аутентификации. Проверьте API ключ."
        return error_msg
    except json.JSONDecodeError:
        return f"Ошибка API (статус {status_code}): {response_text}"