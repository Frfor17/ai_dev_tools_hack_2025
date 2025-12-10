"""Инструмент для создания куба в CAD системе."""

from fastmcp import Context
from pydantic import Field
from mcp.types import TextContent
from .utils import ToolResult
from mcp_instance import mcp
from .tool_create_shapes import _create_shape_impl  # Импортируем helper-функцию, а не инструмент

@mcp.tool(
    name="create_cube",
    description="""
    Создать куб в CAD системе.
    Создает 3D-куб с заданным размером.
    """
)
async def create_cube(
    size: float = Field(
        10.0,
        description="Размер куба в миллиметрах (положительное число)"
    ),
    ctx: Context = None
) -> ToolResult:
    """
    Создать куб в CAD системе.
    
    Args:
        size: Размер куба в миллиметрах (положительное число)
        ctx: Контекст для логирования
    
    Returns:
        ToolResult: Результат выполнения инструмента
    """
    return await _create_shape_impl("cube", size, ctx)