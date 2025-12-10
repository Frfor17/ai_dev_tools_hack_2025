from mcp.server.fastmcp import FastMCP
import httpx
from mcp_instance import mcp
from tool_create_shape import create_shape


@mcp.tool()
async def create_cube(size: float = 10.0) -> str:
    """
    Создать куб в CAD системе.
    
    Аргументы:
    - size: Размер куба в миллиметрах (положительное число)
    """
    return await create_shape("cube", size)