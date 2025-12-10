"""Инструмент для создания сферы в CAD системе."""

from fastmcp import Context
from pydantic import Field
from mcp.types import TextContent
from .utils import ToolResult
from mcp_instance import mcp
from .tool_create_shapes import _create_shape_impl  # Импортируем helper-функцию, а не инструмент

@mcp.tool(
    name="create_sphere",
    description="""
    Создать сферу в CAD системе.
    Создает 3D-сферу с заданным диаметром.
    """
)
async def create_sphere(
    size: float = Field(
        10.0,
        description="Диаметр сферы в миллиметрах (положительное число)"
    ),
    ctx: Context = None
) -> ToolResult:
    """
    Создать сферу в CAD системе.
    
    Args:
        size: Диаметр сферы в миллиметрах (положительное число)
        ctx: Контекст для логирования
    
    Returns:
        ToolResult: Результат выполнения инструмента
    """
    return await _create_shape_impl("sphere", size, ctx)