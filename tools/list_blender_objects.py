"""Инструмент для получения объектов Blender."""

import os
from typing import Dict, Any
from fastmcp import Context
from mcp.types import TextContent
from pydantic import Field
from mcp_instance import mcp
from .utils import ToolResult, _require_env_vars
from cad_client import cad_client

@mcp.tool(
    name="list_blender_objects",
    description="""📝 Получить список объектов из Blender.

Позволяет получить объекты из Blender через REST API.
Требует настройки переменной окружения: BLENDER_API_URL.
Для аутентификации используйте BLENDER_API_TOKEN.
"""
)
async def list_blender_objects(ctx: Context = None) -> ToolResult:
    """
    📝 Получает список объектов из Blender.
    
    Returns:
        ToolResult: Результат с объектами Blender
        
    Raises:
        McpError: При ошибках подключения или отсутствии настроек
    """
    await ctx.info("🚀 Начинаем получение объектов Blender")
    
    try:
        objects_data = await cad_client.get_blender_objects()
        
        # Форматируем результат
        if isinstance(objects_data, list):
            formatted = "\n".join([
                f"- {obj.get('name', 'Без имени')}"
                for obj in objects_data[:10]  # Первые 10 объектов
            ])
            text_content = f"📦 Найдено объектов: {len(objects_data)}\n\n{formatted}"
        else:
            text_content = f"📦 Объекты Blender: {objects_data}"
        
        await ctx.info("✅ Объекты успешно получены")
        
        return ToolResult(
            content=[TextContent(type="text", text=text_content)],
            structured_content={"objects": objects_data},
            meta={"source": "blender"}
        )
        
    except ConnectionError as e:
        await ctx.error(f"❌ Ошибка подключения: {e}")
        raise
    except Exception as e:
        await ctx.error(f"❌ Ошибка при получении объектов: {e}")
        raise