from mcp_instance import mcp
from .tool_create_shapes import create_shape

@mcp.tool()
async def create_sphere(size: float = 10.0) -> str:
    """
    Создать сферу в CAD системе.
    
    Аргументы:
    - size: Диаметр сферы в миллиметрах (положительное число)
    """
    return await create_shape("sphere", size)