from mcp_instance import mcp
from .tool_create_shapes import create_shape

@mcp.tool()
async def create_cylinder(size: float = 10.0) -> str:
    """
    Создать цилиндр в CAD системе.
    
    Аргументы:
    - size: Диаметр цилиндра в миллиметрах (положительное число)
    """
    return await create_shape("cylinder", size)