"""Инструмент для создания цилиндра в CAD системе."""

from typing import Optional
from fastmcp import Context
from pydantic import Field
from mcp.types import TextContent
import math

# Импортируем mcp из единого экземпляра
from mcp_instance import mcp

# Импортируем утилиты
from .utils import ToolResult, get_client, FASTAPI_URL


@mcp.tool(
    name="create_cylinder",
    description="""
    🛢️ Создать цилиндр в CAD системе.
    
    Создает цилиндр с заданным диаметром и высотой.
    """
)
async def create_cylinder(
    size: float = Field(
        10.0,
        description="Диаметр цилиндра в миллиметрах (положительное число)",
        gt=0
    ),
    ctx: Context = None
) -> ToolResult:
    """
    Создает цилиндрическую фигуру в CAD системе.
    
    Args:
        size: Диаметр цилиндра в мм
        ctx: Контекст для логирования
        
    Returns:
        ToolResult: Информация о созданном цилиндре
        
    Examples:
        >>> result = await create_cylinder(15.0)
        >>> print(result.content[0].text)
    """
    if ctx:
        await ctx.info(f"🛢️ Создаем цилиндр диаметром {size} мм...")
        await ctx.report_progress(progress=0, total=100)
    
    client = await get_client()
    try:
        if ctx:
            await ctx.report_progress(progress=25, total=100)
            await ctx.info(f"📡 Отправляем запрос на создание цилиндра...")
        
        # Параметры запроса
        params = {"shape_type": "cylinder", "size": size}
        response = await client.get(f"{FASTAPI_URL}/api/cad/create-shape", params=params)
        response.raise_for_status()
        
        if ctx:
            await ctx.report_progress(progress=50, total=100)
        
        data = response.json()
        
        if ctx:
            await ctx.report_progress(progress=75, total=100)
            await ctx.info(f"✅ Цилиндр успешно создан!")
        
        # Расчет объема цилиндра: V = πr²h
        # Предполагаем высоту равной диаметру, если не указано иное
        height = size  # Высота равна диаметру для базового цилиндра
        radius = size / 2
        volume = math.pi * (radius**2) * height
        
        result_text = (
            f"✅ Цилиндр создан успешно!\n\n"
            f"📐 Тип: Цилиндр\n"
            f"📏 Диаметр: {data.get('parameters', {}).get('size', size)} мм\n"
            f"📏 Высота: {height:.2f} мм\n"
            f"🔵 Радиус: {radius:.2f} мм\n"
            f"🛢️ Объем: {volume:.2f} мм³\n"
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
                "radius": radius,
                "height": height,
                "volume": volume
            },
            meta={
                "shape_type": "cylinder",
                "size": size,
                "endpoint": "/api/cad/create-shape"
            }
        )
        
    except Exception as e:
        error_msg = f"❌ Ошибка при создании цилиндра: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        return ToolResult(
            content=[TextContent(type="text", text=error_msg)],
            structured_content={"error": str(e)},
            meta={
                "shape_type": "cylinder",
                "size": size,
                "endpoint": "/api/cad/create-shape",
                "error": True
            }
        )