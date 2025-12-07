# tools/utils.py
"""Общие утилиты для инструментов."""

import os
from typing import List, Dict, Any, Optional
from mcp.types import TextContent
from mcp.shared.exceptions import McpError, ErrorData

class ToolResult:
    """Результат выполнения инструмента."""
    
    def __init__(
        self,
        content: List[TextContent],
        structured_content: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.structured_content = structured_content or {}
        self.meta = meta or {}

def _require_env_vars(names: list[str]) -> dict[str, str]:
    """
    Проверяет наличие обязательных переменных окружения.
    
    Args:
        names: Список имен переменных окружения
        
    Returns:
        Словарь с переменными окружения
        
    Raises:
        McpError: Если отсутствуют обязательные переменные
    """
    missing = [n for n in names if not os.getenv(n)]
    if missing:
        raise McpError(
            ErrorData(
                code=-32602,
                message="Отсутствуют обязательные переменные окружения: " + ", ".join(missing)
            )
        )
    return {n: os.getenv(n, "") for n in names}