"""Инструмент для создания сферы в CAD системе."""

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
    name="create_sphere",
    description="""
    ⚽ Создать сферу в CAD системе.
    
    Создает сферу с заданным диаметром.
    """
)
async def create_sphere(
    size: float = Field(
        10.0,
        description="Диаметр сферы в миллиметрах (положительное число)",
        gt=0
    ),
    ctx: Context = None
) -> ToolResult:
    """
    Создает сферическую фигуру в CAD системе.
    
    Args:
        size: Диаметр сферы в мм
        ctx: Контекст для логирования
        
    Returns:
        ToolResult: Информация о созданной сфере
        
    Examples:
        >>> result = await create_sphere(15.0)
        >>> print(result.content[0].text)
    """
    if ctx:
        await ctx.info(f"⚽ Создаем сферу диаметром {size} мм...")
        await ctx.report_progress(progress=0, total=100)
    
    client = await get_client()
    try:
        if ctx:
            await ctx.report_progress(progress=25, total=100)
            await ctx.info(f"📡 Отправляем запрос на создание сферы...")
        
        # Параметры запроса
        params = {"shape_type": "sphere", "size": size}
        response = await client.get(f"{FASTAPI_URL}/api/cad/create-shape", params=params)
        response.raise_for_status()
        
        if ctx:
            await ctx.report_progress(progress=50, total=100)
        
        data = response.json()
        
        if ctx:
            await ctx.report_progress(progress=75, total=100)
            await ctx.info(f"✅ Сфера успешно создана!")
        
        # Расчет объема сферы: V = (4/3)πr³
        radius = size / 2
        volume = (4/3) * math.pi * (radius**3)
        
        result_text = (
            f"✅ Сфера создана успешно!\n\n"
            f"📐 Тип: Сфера\n"
            f"📏 Диаметр: {data.get('parameters', {}).get('size', size)} мм\n"
            f"🔵 Радиус: {radius:.2f} мм\n"
            f"⚪ Объем: {volume:.2f} мм³\n"
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
                "volume": volume
            },
            meta={
                "shape_type": "sphere",
                "size": size,
                "endpoint": "/api/cad/create-shape"
            }
        )
        
    except Exception as e:
        error_msg = f"❌ Ошибка при создании сферы: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        return ToolResult(
            content=[TextContent(type="text", text=error_msg)],
            structured_content={"error": str(e)},
            meta={
                "shape_type": "sphere",
                "size": size,
                "endpoint": "/api/cad/create-shape",
                "error": True
            }
        )