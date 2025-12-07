"""Инструмент для создания фигур в CAD."""

import os
from typing import Dict, Any
from fastmcp import Context
from mcp.types import TextContent
from pydantic import Field
from mcp_instance import mcp
from .utils import ToolResult, _require_env_vars
from cad_client import cad_client

@mcp.tool(
    name="create_shape",
    description="""📝 Создать простую фигуру в CAD.

Создает базовые 3D-фигуры: куб, сфера, цилиндр, конус.
Поддерживается настройка размера фигуры.
"""
)
async def create_shape(
    shape_type: str = Field(
        default="cube",
        description="Тип фигуры: cube, sphere, cylinder, cone"
    ),
    size: float = Field(
        default=1.0,
        description="Размер фигуры (должен быть положительным)",
        gt=0
    ),
    ctx: Context = None
) -> ToolResult:
    """
    📝 Создает простую фигуру в CAD системе.
    
    Args:
        shape_type: Тип создаваемой фигуры
        size: Размер фигуры
        
    Returns:
        ToolResult: Результат создания фигуры
        
    Raises:
        McpError: При ошибках создания или неверных параметрах
    """
    await ctx.info(f"🚀 Начинаем создание фигуры: {shape_type}, размер: {size}")
    await ctx.report_progress(progress=0, total=100)
    
    try:
        await ctx.info("🔍 Проверяем параметры")
        await ctx.report_progress(progress=25, total=100)
        
        await ctx.info(f"🛠️ Создаем фигуру {shape_type}")
        result = await cad_client.create_simple_shape(shape_type, size)
        await ctx.report_progress(progress=75, total=100)
        
        await ctx.info("📝 Форматируем результат")
        text_content = f"✅ {result['message']}\n\n📊 Детали:\n- Тип: {result['shape_type']}\n- Размер: {result['size']}\n- Статус: {result['status']}"
        await ctx.report_progress(progress=100, total=100)
        
        await ctx.info("🎉 Фигура успешно создана")
        
        return ToolResult(
            content=[TextContent(type="text", text=text_content)],
            structured_content=result,
            meta={"operation": "create_shape"}
        )
        
    except ValueError as e:
        await ctx.error(f"❌ Ошибка валидации: {e}")
        raise
    except Exception as e:
        await ctx.error(f"❌ Ошибка при создании фигуры: {e}")
        raise