"""Инструмент для получения списка документов CAD."""

import os
from typing import Dict, Any
from fastmcp import Context
from mcp.types import TextContent
from pydantic import Field
from mcp_instance import mcp
from .utils import ToolResult, _require_env_vars
from cad_client import cad_client

@mcp.tool(
    name="list_cad_documents",
    description="""📝 Получить список документов из CAD системы Onshape.

Позволяет получить первые 5 документов из вашего аккаунта Onshape.
Требует настройки переменных окружения: ONSHAPE_API_URL, ONSHAPE_ACCESS_KEY, ONSHAPE_SECRET_KEY.
"""
)
async def list_cad_documents(ctx: Context = None) -> ToolResult:
    """
    📝 Получает список документов из CAD системы Onshape.
    
    Returns:
        ToolResult: Результат с документами Onshape
        
    Raises:
        McpError: При ошибках подключения или отсутствии настроек
    """
    await ctx.info("🚀 Начинаем получение документов Onshape")
    
    try:
        documents = await cad_client.get_onshape_documents()
        
        # Форматируем результат
        if documents:
            formatted = "\n".join([
                f"- {doc['name']} (ID: {doc['id']})"
                for doc in documents
            ])
            text_content = f"📄 Найдено документов: {len(documents)}\n\n{formatted}"
        else:
            text_content = "📭 Документы не найдены"
        
        await ctx.info("✅ Документы успешно получены")
        
        return ToolResult(
            content=[TextContent(type="text", text=text_content)],
            structured_content={"documents": documents},
            meta={"source": "onshape"}
        )
        
    except Exception as e:
        await ctx.error(f"❌ Ошибка при получении документов: {e}")
        raise