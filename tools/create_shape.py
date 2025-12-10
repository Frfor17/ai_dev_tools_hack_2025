"""Инструмент для создания 3D-фигур в CAD системе."""

from typing import Optional
from fastmcp import Context
from pydantic import Field
from mcp.types import TextContent

# Импортируем mcp из единого экземпляра
from mcp_instance import mcp

# Импортируем утилиты
from .utils import ToolResult, get_client, FASTAPI_URL


@mcp.tool(
    name="create_cad_shape",
    description="""
    🏗️ Создать 3D-фигуру в CAD системе.
    
    Создает базовые 3D-фигуры: кубы, сферы и цилиндры.
    Позволяет задавать размер фигуры в миллиметрах.
    """
)
async def create_shape(
    shape_type: str = Field(
        ...,
        description="Тип создаваемой фигуры: cube (куб), sphere (сфера), cylinder (цилиндр)"
    ),
    size: float = Field(
        10.0,
        description="Размер фигуры в миллиметрах (положительное число)",
        gt=0
    ),
    ctx: Context = None
) -> ToolResult:
    """
    Создает 3D-фигуру в CAD системе с указанными параметрами.
    
    Args:
        shape_type: Тип фигуры (cube/sphere/cylinder)
        size: Размер фигуры в мм
        ctx: Контекст для логирования и отслеживания прогресса
        
    Returns:
        ToolResult: Информация о созданной фигуре
        
    Raises:
        ValueError: При недопустимых параметрах
        Exception: При ошибке создания фигуры
        
    Examples:
        >>> result = await create_shape("cube", 15.0)
        >>> print(result.content[0].text)
    """
    if ctx:
        await ctx.info(f"🏗️ Начинаем создание фигуры типа '{shape_type}'...")
        await ctx.report_progress(progress=0, total=100)
    
    # Валидация параметров
    valid_shapes = ["cube", "sphere", "cylinder"]
    shape_type_lower = shape_type.lower()
    
    if shape_type_lower not in valid_shapes:
        error_msg = f"❌ Неподдерживаемый тип фигуры '{shape_type}'. Используйте: {', '.join(valid_shapes)}"
        if ctx:
            await ctx.error(error_msg)
        return ToolResult(
            content=[TextContent(type="text", text=error_msg)],
            structured_content={"error": "invalid_shape_type", "valid_shapes": valid_shapes},
            meta={"shape_type": shape_type, "error": True}
        )
    
    client = await get_client()
    try:
        if ctx:
            await ctx.report_progress(progress=25, total=100)
            await ctx.info(f"📡 Отправляем запрос на создание фигуры...")
        
        # Параметры запроса
        params = {"shape_type": shape_type_lower, "size": size}
        response = await client.get(f"{FASTAPI_URL}/api/cad/create-shape", params=params)
        response.raise_for_status()
        
        if ctx:
            await ctx.report_progress(progress=50, total=100)
        
        data = response.json()
        
        if ctx:
            await ctx.report_progress(progress=75, total=100)
            await ctx.info(f"✅ Фигура успешно создана!")
        
        result_text = (
            f"✅ Фигура создана успешно!\n\n"
            f"📐 Тип: {data.get('parameters', {}).get('shape_type', 'неизвестно')}\n"
            f"📏 Размер: {data.get('parameters', {}).get('size', 'неизвестно')} мм\n"
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
                "id": data.get('id')
            },
            meta={
                "shape_type": shape_type,
                "size": size,
                "endpoint": "/api/cad/create-shape"
            }
        )
        
    except Exception as e:
        error_msg = f"❌ Ошибка при создании фигуры: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        return ToolResult(
            content=[TextContent(type="text", text=error_msg)],
            structured_content={"error": str(e)},
            meta={
                "shape_type": shape_type,
                "size": size,
                "endpoint": "/api/cad/create-shape",
                "error": True
            }
        )