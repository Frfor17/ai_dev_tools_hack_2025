"""Инструмент для создания куба в CAD системе."""

from typing import Optional
from fastmcp import Context
from pydantic import Field
from mcp.types import TextContent

# Импортируем mcp из единого экземпляра
from mcp_instance import mcp

# Импортируем утилиты
from .utils import ToolResult, get_client, FASTAPI_URL


@mcp.tool(
    name="create_cube",
    description="""
    🧊 Создать куб в CAD системе.
    
    Создает куб с заданным размером стороны.
    """
)
async def create_cube(
    size: float = Field(
        10.0,
        description="Длина стороны куба в миллиметрах (положительное число)",
        gt=0
    ),
    ctx: Context = None
) -> ToolResult:
    """
    Создает кубическую фигуру в CAD системе.
    
    Args:
        size: Длина стороны куба в мм
        ctx: Контекст для логирования
        
    Returns:
        ToolResult: Информация о созданном кубе
        
    Examples:
        >>> result = await create_cube(15.0)
        >>> print(result.content[0].text)
    """
    if ctx:
        await ctx.info(f"🧊 Создаем куб размером {size} мм...")
        await ctx.report_progress(progress=0, total=100)
    
    client = await get_client()
    try:
        if ctx:
            await ctx.report_progress(progress=25, total=100)
            await ctx.info(f"📡 Отправляем запрос на создание куба...")
        
        # Параметры запроса
        params = {"shape_type": "cube", "size": size}
        response = await client.get(f"{FASTAPI_URL}/api/cad/create-shape", params=params)
        response.raise_for_status()
        
        if ctx:
            await ctx.report_progress(progress=50, total=100)
        
        data = response.json()
        
        if ctx:
            await ctx.report_progress(progress=75, total=100)
            await ctx.info(f"✅ Куб успешно создан!")
        
        result_text = (
            f"✅ Куб создан успешно!\n\n"
            f"📐 Тип: Куб\n"
            f"📏 Размер: {data.get('parameters', {}).get('size', size)} мм\n"
            f"📦 Объем: {size**3} мм³\n"
            f"🎯 Результат: {data.get('result', 'успешно')}\n"
            f"🆔 ID: {data.get('id', 'не указан')}"
        )
        
        if ctx:
            await ctx.report_progress(progress=100, total=100)
        
        return ToolResult(
            content=[TextContent(type="text", text=result_text)],
            structured_content={
                "parameters": data.get('parameters', {}),
                "result": data.get('result'),
                "id": data.get('id'),
                "volume": size**3
            },
            meta={
                "shape_type": "cube",
                "size": size,
                "endpoint": "/api/cad/create-shape"
            }
        )
        
    except Exception as e:
        error_msg = f"❌ Ошибка при создании куба: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        return ToolResult(
            content=[TextContent(type="text", text=error_msg)],
            structured_content={"error": str(e)},
            meta={
                "shape_type": "cube",
                "size": size,
                "endpoint": "/api/cad/create-shape",
                "error": True
            }
        )