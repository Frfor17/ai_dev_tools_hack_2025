from fastmcp import FastMCP
from common_logic import cad_client
import asyncio

mcp = FastMCP("CAD Integration Server", dependencies=["httpx"])

@mcp.tool
async def list_cad_documents() -> str:
    """Получить список документов из CAD системы."""
    return await cad_client.get_onshape_documents()

@mcp.tool
async def list_blender_objects() -> str:
    """Получить список объектов из Blender."""
    return await cad_client.get_blender_objects()

@mcp.tool
async def create_shape(shape_type: str = "cube", size: float = 1.0) -> str:
    """
    Создать простую фигуру в CAD.
    
    Args:
        shape_type: Тип фигуры (cube, sphere, cylinder, cone)
        size: Размер фигуры
    """
    return await cad_client.create_simple_shape(shape_type, size)

@mcp.tool
async def cad_systems_info() -> str:
    """Получить информацию о доступных CAD системах."""
    info = []
    
    if cad_client.onshape_key:
        info.append("✅ Onshape: настроен")
    else:
        info.append("❌ Onshape: не настроен (добавьте ключи в .env)")
        
    if cad_client.blender_url:
        info.append("✅ Blender API: настроен")
    else:
        info.append("❌ Blender API: не настроен")
        
    return "\n".join(info)

if __name__ == "__main__":
    print("CAD MCP Server запущен. Подключайте к VS Code.")
    print("Проверьте настройки API в файле .env")
    mcp.run()